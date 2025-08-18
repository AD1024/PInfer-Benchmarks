import strands
import os
import json
import math
from constants import benchmarks

# MODEL_ID = 'us.anthropic.claude-3-7-sonnet-20250219-v1:0'
ERROR_CORRECTION = False

class AgentWrapper:
    def __init__(self, agent: strands.Agent):
        self.agent = agent
        self.num_invocations = 0
        self.num_input_tokens = 0
        self.num_output_tokens = 0
        self.total_cycles = 0
        self.total_tokens = 0

    def __call__(self, prompt: str, **kwargs):
        result = self.agent(prompt, **kwargs)
        self.num_invocations += 1
        metrics = result.metrics.get_summary()
        self.num_input_tokens += metrics.get('accumulated_usage', {}).get('inputTokens', 0)
        self.num_output_tokens += metrics.get('accumulated_usage', {}).get('outputTokens', 0)
        self.total_tokens += metrics.get('accumulated_usage', {}).get('totalTokens', 0)
        self.total_cycles = metrics.get('total_cycles', 0)
        return result
    
    def clear_history(self):
        self.agent.messages = []

    def get_summary(self):
        return {
            'num_invocations': self.num_invocations,
            'num_input_tokens': self.num_input_tokens,
            'num_output_tokens': self.num_output_tokens,
            'total_cycles': self.total_cycles,
            'total_tokens': self.total_tokens
        }


def load_system_prompt(p_model: str, top_k=20):
    with open('p_basics.txt', 'r') as file:
        system_prompt = file.read()
    
    with open('p_infer_specs.txt', 'r') as file:
        infer_specs = file.read()

    task_description = "You are an expert in analyzing P models and deciding importance of specifications based on their criticalness to the correctness of the P model."\
                        "A specification is more critical if it is central to the correctness of the protocol rather than asserting properties about the low-level implementation details."\
                        "Correctness properties could be Atomicity, Isolation, Consistency, etc."\
                        f"You will be given a P model and a set of likely specifications. Your task is to pick to most important {top_k} specifications.\n"\
                        + p_model
    
    return system_prompt, infer_specs, task_description

def create_agent(model_id: str, model_prompt: str, top_k=20, with_task=True):
    system_prompt, infer_specs, task = load_system_prompt(model_prompt, top_k)
    
    from strands.models import BedrockModel
    model = BedrockModel(model_id=model_id, region_name='us-east-1')
    agent = AgentWrapper(strands.Agent(
        system_prompt=system_prompt + '\n' + infer_specs + ('\n' + task if with_task else model_prompt),
        model=model
    ))
    
    return agent

def check_prerequisites(benchmark):
    """Check if the necessary files for the benchmark exist."""
    required_files = [
        'pruned_invariants.txt',
        'PSrc'
    ]
    for file in required_files:
        if not os.path.exists(os.path.join(benchmark, file)):
            print(f"Missing required file: {file} in benchmark {benchmark}")
            return False
    return True

def read_p_model(benchmark: str):
    # read benchmark/PSrc
    f_to_src = {}
    for (root, dirs, files) in os.walk(os.path.join(benchmark, 'PSrc')):
        for f in files:
            if f.endswith('.p'):
                with open(os.path.join(root, f), 'r') as file:
                    p_model = file.read()
                f_to_src[f] = p_model
    prompt = "Here are the files in the P model:\n"
    for (fname, src) in f_to_src.items():
        prompt += f"<{fname}>\n{src}\n"
    return prompt

def read_specs(benchmark: str):
    # read benchmark/pruned_invariants.txt
    with open(os.path.join(benchmark, 'pruned_invariants.txt'), 'r') as file:
        return file.readlines()

def rank_monolithic(agent: AgentWrapper, specs: list, top_k: int, retries=3):
    prompt = "\nHere are likely specifications for the P model:\n" + "\n".join(specs) + "\n" + \
            f"Please give the most important {top_k} of these specifications based on their importance to the P model. Give the specifications separated by newlines. PLEASE DO NOT OUTPUT OTHER TEXTS OR FORMULAS NOT IN THE GIVEN LIST OF SPECIFICATIONS.\n" + \
            "If you cannot find any important specifications, just return an empty string."
    specs = [spec.strip() for spec in specs if spec.strip()]
    result = []
    while retries > 0:
        resp = agent(prompt)
        ranked = resp.message.get("content", [])
        retries -= 1
        if ranked:
            response_text = "\n".join(item.get("text", "") for item in ranked if isinstance(item, dict) and "text" in item)
            if response_text.strip():
                props = list(filter(lambda x: x != '', (response_text.strip()).split('\n')))
                result += [prop for prop in props if prop in specs]
                if all(prop in specs for prop in props) or not ERROR_CORRECTION:
                    return result
                not_in_specs = [prop for prop in props if prop not in specs]
                print(f"{not_in_specs} are not in the original list of specifications.")
                prompt = f"Some of the specifications you returned are not in the original list: {not_in_specs}. Try again to choose {top_k - len(result)} more specifications from the list of specifications given below.\n" + \
                        "\n".join((prop for prop in specs if prop not in result))
        else:
            prompt = 'Your results must not be empty.'
    return []

def cluster_specs_by_quantifiers(specs: list):
    clusters = {}
    def parse_header(spec: str):
        forall = '∀'
        exists = '∃'
        quantifiers = []
        i = 0
        def consume_space(s, p):
            while p < len(s) and s[p] == ' ':
                p += 1
            return p
        while i < len(spec):
            if spec[i] in {forall, exists}:
                # parse event type
                j = i + 1
                while j < len(spec) and spec[j] != ':':
                    j += 1
                j = consume_space(spec, j + 1)
                s = j
                while j < len(spec) and spec[j] not in {' ', ':'}:
                    j += 1
                event_type = spec[s:j]
                quantifiers.append(event_type)
                i = j
            else:
                i += 1
        return quantifiers

    for spec in specs:
        quantifiers = parse_header(spec)
        cluster = tuple(quantifiers)
        if cluster not in clusters:
            clusters[cluster] = []
        clusters[cluster].append(spec)
    assert sum(len(v) for v in clusters.values()) == len(specs), "Clustered specifications do not match the original list."
    return clusters

def rank_clustering(agent: AgentWrapper, specs: list):
    clusters = cluster_specs_by_quantifiers(specs)
    # print(clusters)
    messages = []
    result = []
    prompt_template = "Select most important specifications for the following cluster of specifications:\n\n{}\n\n. Give the specifications separated by newlines. PLEASE DO NOT OUTPUT OTHER TEXTS OR FORMULAS NOT IN THE GIVEN LIST OF SPECIFICATIONS.\nIf you cannot find any important specifications, just return an empty string."
    for cluster, specs in clusters.items():
        prompt = prompt_template.format("\n".join(specs))
        messages.append(prompt)
        response = agent(prompt)
        contents = response.message.get("content", [])
        if contents:
            response_text = "\n".join(item.get("text", "") for item in contents if isinstance(item, dict) and "text" in item)
            if response_text.strip():
                props = (response_text.strip()).split('\n')
                result += props
    return result

def rank_individual_llm_call(agent: AgentWrapper, prompt: str, current_set: set, current_inv: str, top_k) -> str | None:
    response = agent(prompt)
    contents = response.message.get("content", [])
    responses = [item.get("text", "") for item in contents if isinstance(item, dict) and "text" in item]
    print(f"Current spec: {current_inv}")
    for resp in responses:
        resp = resp.strip()
        if resp == 'skip':
            print(f"Skipped")
            return None
        elif resp == 'add':
            print(f"Adding")
            if len(current_set) < top_k:
                current_set.add(current_inv)
                return None
            else:
                return f"Cannot add {current_inv} to current set, as it exceeds the limit of {top_k} specifications."
        else:
            assert resp.startswith('replace ')
            inv = resp[len('replace '):].strip()
            print(f"Replacing {inv}")
            if inv in current_set:
                current_set.remove(inv)
                current_set.add(current_inv)
                return None
            else:
                return f"Cannot remove {inv} from current set, as it is not present in the current set."

def rank_individual(agent: AgentWrapper, specs: list, top_k=20, max_retries=3):
    current_set = set()
    prompt = f"You are given a set of specifications S that has already been selected and a specification I to work on. Your task is to decide whether I should be added to S or not. Since the goal is to choose top {top_k} specifications, you should keep |S| <= {top_k}. Your response should be in the format of: `add` or `skip` or `replace <spec>`. `add` will add I to S, and can only be used when |S| < {top_k}. `replace <spec>` will replace <spec> in S by I can can only be called with <spec> in S. If you cannot decide, just return `skip`. DO NOT OUTPUT OTHER TEXTS OR FORMULAS NOT IN THE GIVEN LIST OF SPECIFICATIONS."

    for spec in specs:
        curr_prompt = f"{prompt}\n\nCurrent set of specifications:\n{current_set}\n\nSpecification to work on:\n{spec}\n"
        retry = max_retries
        success = False
        retry_prompt = ''
        while retry > 0 and not success:
            retry_prompt = rank_individual_llm_call(agent, curr_prompt + retry_prompt, current_set, spec, top_k)
            if not retry_prompt:
                success = True
                break
        if not success:
            raise Exception(f"Failed to get a response for specification: {spec} after {max_retries} retries.")
        
    return list(current_set)

def check_goal(benchmark: str, specs: list):
    goal_file = os.path.join(benchmark, 'confirmed_specs.txt')
    if not os.path.exists(goal_file):
        print(f"No goal file found for benchmark {benchmark}.")
        return {}, {}
    with open(goal_file, 'r') as file:
        confirmed_specs = file.readlines()
    confirmed_specs = set(spec.strip() for spec in confirmed_specs if spec.strip())
    filtered_specs = set(spec.strip() for spec in specs if spec.strip())
    found = {spec for spec in confirmed_specs if spec in filtered_specs}
    not_found = confirmed_specs - found
    return found, not_found

def rank_and_check(model, benchmark, top_k=20, mode='monolithic', max_retries=3):
    print(f"Ranking specifications for benchmark: {benchmark}")
    if not check_prerequisites(benchmark):
        print(f"Skipping {benchmark} due to missing prerequisites.")
        return None
    
    p_model = read_p_model(benchmark)
    agent = create_agent(model, p_model, top_k)
    specs = read_specs(benchmark)
    if not specs:
        print(f"No specifications found for benchmark: {benchmark}")
        return None
    result = []
    import datetime
    start = datetime.datetime.now()
    match mode:
        case 'clustering':
            result = rank_clustering(agent, specs)
        case 'monolithic':
            result = rank_monolithic(agent, specs, top_k, max_retries)
        case 'individual':
            result = rank_individual(agent, specs, top_k, max_retries)
        case _:
            raise ValueError(f"Unknown ranking mode: {mode}")
    end = datetime.datetime.now()
    delta = (end - start).total_seconds()
    found, not_found = check_goal(benchmark, result)
    summary = agent.get_summary()
    if found or not_found:
        print(f"Found {len(found)} specifications in the goal:\n {'\n'.join(found)}")
        print(f"Not found {len(not_found)} specifications in the goal:\n{'\n'.join(not_found)}")
        print(f"%Found: {len(found) / (len(found) + len(not_found)):.2f}")
        summary['found_goals'] = len(found)
        summary['total_goals'] = len(found) + len(not_found)
        summary['not_found_goals'] = len(not_found)
        summary['found_goals_raw'] = list(found)
        summary['not_found_goals_raw'] = list(not_found)
        summary['duration'] = delta
    else:
        print(f"No confirmed specifications found in the goal for benchmark: {benchmark}")
    return summary

def rank_by_score_all( example_benchmark: str, benchmarks: list[str], chunk_size=10):
    models = ['us.anthropic.claude-3-7-sonnet-20250219-v1:0',
              'us.anthropic.claude-3-5-sonnet-20241022-v2:0',
              'us.anthropic.claude-sonnet-4-20250514-v1:0']
    summary = {}
    for m in models:
        summary[m] = {}
        for b in benchmarks:
            summary[m][b] = {}
            try:
                specs = read_specs(b)
                if not specs:
                    print(f"No specifications found for benchmark: {b}")
                    continue
                result = rank_by_score(m, example_benchmark, b, specs, top_k=20, chunk_size=chunk_size)
                summary[m][b] = result
                with open(f'rank_summary_smoke_scoring.json', 'w') as f:
                    json.dump(summary, f, indent=4)
            except Exception as e:
                print(f"Exception occurred while processing benchmark {b} with model {m}: {e}")
                summary[m][b] = {'error': str(e)}
                with open(f'rank_summary_smoke_scoring.json', 'w') as f:
                    json.dump(summary, f, indent=4)
                continue

def smoke_test(benchmarks, executable, percentage=False):
    # top_k = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
    top_k = [10, 20, 30, 40, 50, 60]
    # benchmarks = ['firewall']
    models = [
              'us.anthropic.claude-3-7-sonnet-20250219-v1:0',
              'us.anthropic.claude-3-5-sonnet-20241022-v2:0',
              'us.anthropic.claude-sonnet-4-20250514-v1:0']
    top_level_summary = {}
    all_found = {}
    for mod in models:
        top_level_summary[mod] = {}
        all_found[mod] = set()
        for k in top_k:
            top_level_summary[mod][k] = {}
            print(f'========Testing model {mod} with top_k={k}========')
            for b in benchmarks:
                try:
                    specs = read_specs(b)
                    if percentage:
                        k_val = int(len(specs) * k / 100)
                    else:
                        k_val = k
                    if b in all_found[mod]:
                        print(f"Skipping benchmark {b} for model {mod} ... already found all previously")
                        continue
                    summary = executable(mod, b, top_k=k_val, mode='monolithic', max_retries=3)
                    if summary is None:
                        print(f"Skipping benchmark {b} for model {mod} due to errors.")
                        top_level_summary[mod][k][b] = {'error': 'Prerequisites not met or no specifications found.'}
                    elif summary['found_goals'] == summary['total_goals']:
                        print(f"Found all goals for benchmark {b} with model {mod}.")
                        all_found[mod].add(b)
                    top_level_summary[mod][k][b] = summary
                    with open(f'rank_summary_smoke.json', 'w') as f:
                        json.dump(top_level_summary, f, indent=4)
                except Exception as e:
                    print(f"Exception occurred while processing benchmark {b} with model {mod}: {e}")
                    top_level_summary[mod][k][b] = {'error': str(e)}
                    with open(f'rank_summary_smoke.json', 'w') as f:
                        json.dump(top_level_summary, f, indent=4)
                    continue
    return top_level_summary

def load_example(benchmark):
    prompt = f"Here is an example of {benchmark} explaining the strategy of ranking specifications:\n"
    prompt += "\nNow we explain the ranking strategy using this example.\n"
    with open('ranking_example.txt', 'r') as file:
        example = file.read()
    prompt += example
    return prompt

def one_shot_ranking(model_id: str, example_benchmark: str, benchmark: str, top_k=20):
    system_prompt, infer_specs, task_desc = load_system_prompt(read_p_model(benchmark), top_k)
    example = load_example(example_benchmark)
    prompt = f"{system_prompt}\n{infer_specs}\n{example}\n{task_desc}\n\n"
    from strands.models import BedrockModel
    model = BedrockModel(model_id=model_id, region_name='us-east-1')
    agent = AgentWrapper(strands.Agent(
        system_prompt=prompt,
        model=model
    ))
    specs = read_specs(benchmark)
    if not specs:
        print(f"No specifications found for benchmark: {benchmark}")
        return None
    prompt += "Here are likely specifications for the P model:\n" + "\n".join(specs) + "\n" + \
            f"Please give the most important {top_k} of these specifications based on their importance to the P model. Output contents in the required format ONLY (NO MARKDOWN FORMATTING, NO THOUGHT PROCESS, NO OTHER EXPLANATIONS). DO NOT OUTPUT OTHER TEXTS OR FORMULAS NOT IN THE GIVEN LIST OF SPECIFICATIONS.\n"
    specs = [spec.strip() for spec in specs if spec.strip()]
    result = agent(prompt)
    contents = result.message.get("content", [])
    # LLM respond with a json format
    if contents:
        output = contents[0].get("text", "").split('\n')
        identified_specs = []
        i = 0
        while i < len(output):
            # in the following format
            # Rank: [number]
            # Specification: [formal specification]
            # Correctness Confidence: [0.0-1.0]
            # Criticalness Confidence: [0.0-1.0]
            if len(output[i].strip()) == 0:
                i += 1
                continue
            if not output[i].startswith('Rank: '):
                i += 1
                continue
            entry = {}
            rank = output[i].strip()
            spec = output[i + 1].strip()
            correctness_confidence = output[i + 2].strip()
            criticalness_confidence = output[i + 3].strip()
            if rank.startswith('Rank: '):
                entry['rank'] = int(rank[len('Rank: '):].strip())
            if spec.startswith('Specification: '):
                entry['specification'] = spec[len('Specification: '):].strip()
            if correctness_confidence.startswith('Correctness Confidence: '):
                entry['correctness_confidence'] = float(correctness_confidence[len('Correctness Confidence: '):].strip())
            if criticalness_confidence.startswith('Criticalness Confidence: '):
                entry['criticalness_confidence'] = float(criticalness_confidence[len('Criticalness Confidence: '):].strip())
            entry['overall_score'] = entry['correctness_confidence'] * entry['criticalness_confidence']
            identified_specs.append(entry)
            i += 4

        found, not_found = check_goal(benchmark, [entry['specification'] for entry in identified_specs])
        summary = agent.get_summary()
        if found or not_found:
            print(f"Found {len(found)} specifications in the goal:\n {'\n'.join(found)}")
            print(f"Not found {len(not_found)} specifications in the goal:\n{'\n'.join(not_found)}")
            print(f"%Found: {len(found) / (len(found) + len(not_found)):.2f}")
            summary['found_goals'] = len(found)
            summary['total_goals'] = len(found) + len(not_found)
            summary['not_found_goals'] = len(not_found)
            summary['found_goals_raw'] = [entry for entry in identified_specs if entry['specification'] in found]
            summary['not_found_goals_raw'] = list(not_found)
        return summary

def rank_by_score(model_id: str, example_benchmark: str, benchmark: str, specs: list[str], top_k=20, chunk_size=10):
    """Rank specifications by their overall score."""
    example_prompt = load_example(example_benchmark)
    system_prompt, infer_specs, _ = load_system_prompt(read_p_model(benchmark), top_k)
    task_desc = """
You will be given a set of specifications.
For each specification, return the confidence score between 0 (least confident) and 100 (most confident) about whether the specification is true.
If you are sure that the specification is not true, then this score must be 0.
If you are sure that the specification is definitely true, then this score must be 100.
You should also return the criticalness score between 0 (least critical) and 1 (most critical) about whether it is directly related to the protocol rather than the low-level implementation details of
the P model.
If you are sure that the specification is not critical, then this score must be 0.
If you are sure that the specification is a correctness / safety / liveness specification, then this score must be 100.
For each specification, return the result in the following format.
<specification><sep><Correctness Confidence Score between 0 and 100><sep><Criticalness Confidence Score between 0 and 100>
where <sep> is a dollar ($) sign. <specification> MUST be one of the specifications you are given.
Separate results of each specification with a newline. Do not output other texts.
"""
    prompt = f"{system_prompt}\n{infer_specs}\n{example_prompt}\n{task_desc}\n\n"
    from strands.models import BedrockModel
    model = BedrockModel(model_id=model_id, region_name='us-east-1')
    agent = AgentWrapper(strands.Agent(
        system_prompt=prompt,
        model=model,
        callback_handler=None,
    ))
    if not specs:
        print(f"No specifications found for benchmark: {benchmark}")
        return None
    spec_summary = {}
    i = 0
    while i < len(specs):
        subchunk = specs[i:min(i + chunk_size, len(specs))]
        num_chunk = min(i + chunk_size, len(specs)) - i
        i += chunk_size
        subchunk = [spec.strip() for spec in subchunk if spec.strip()]
        print(f"Processing chunk {i // chunk_size}/{math.ceil(len(specs) / chunk_size)} with {num_chunk} specifications.")
        agent.clear_history()
        response = agent(f"Specifications:\n{'\n'.join(subchunk)}\n")
        contents = response.message.get("content", [])
        if contents:
            response_text = "\n".join(item.get("text", "") for item in contents if isinstance(item, dict) and "text" in item)
            if response_text.strip():
                lines = response_text.strip().split('\n')
                for line in lines:
                    if line.strip():
                        parts = line.split('$')
                        if len(parts) >= 2:
                            spec_id = parts[0].strip()
                            correctness_confidence = float(parts[1])
                            criticalness_confidence = float(parts[2])
                            # assert spec_id in subchunk, f"Specification {spec_id} not found in the current chunk."
                            spec_summary[spec_id] = {
                                'correctness_confidence': correctness_confidence,
                                'criticalness_confidence': criticalness_confidence,
                                'overall_score': correctness_confidence * criticalness_confidence
                            }
                        else:
                            print(f"Unexpected format in response: {line}")
            else:
                print(f"No valid content returned for chunk {i // chunk_size}.")
    
    sorted_specs = sorted(spec_summary.items(), key=lambda x: x[1]['overall_score'], reverse=True)
    summary = agent.get_summary()
    # compute cumulative goal coverage
    try:
        with open(os.path.join(benchmark, 'confirmed_specs.txt'), 'r') as file:
            confirmed_specs = file.readlines()
        confirmed_specs = set(spec.strip() for spec in confirmed_specs if spec.strip())
        y_axis = []
        x_axis = []
        found = set()
        found_raw = []
        raw = []
        i = 0
        total = len(sorted_specs)
        for spec in sorted_specs:
            spec_name = spec[0].strip()
            i += 1
            raw.append((i, spec))
            if spec_name in confirmed_specs and spec_name not in found:
                found.add(spec_name)
                found_raw.append((i, spec))
            x_axis.append(i / total)
            y_axis.append(len(found) / len(confirmed_specs))
        summary['cumulative_goal_coverage'] = {
            'x_axis': x_axis,
            'y_axis': y_axis,
            'total_goals': len(confirmed_specs),
            'found_raw': found_raw
        }
        with open(f'raw_rank_{benchmark}.json', 'w') as f:
            json.dump(raw, f, indent=4)
        return summary
    except FileNotFoundError as e:
        print(f"No confirmed specifications found for benchmark: {benchmark}.")
        raise e

    

def explain_invariants(benchmark, agent, invariants):
    prompt = "You will be given some specifications you have selected for the P model you just saw. For each specification, " \
    "provide a confidence score between 0 (least confident) and 1 (most confident) about whether the specification is true" \
    "(If you are sure that the specification is not true, then this score must be 0. If you are sure that the specification is definitely true, the must be 1), "\
    "a confidence score between 0 (least confident) and 1 (most confident) about whether it is directly related to the protocol " \
    "rather than the low-level implementation details of the P model." \
    "and a brief explanation about its semantics," \
    "Output must be in the following format: <Correctness Confidence Score between 0 and 1><newline><Criticalness Confidence Score between 0 and 1><newline><Explanation in English>." \
    "If either of your confience score is low (<0.5), you must also explain in <Explanation in English> why you are not confident about the specification. Wrap around the explanation about your confidence with `**`. If you are confidence about both, then you don't need to include the additional explanations." \
    "Output only these fields in three lines. Do not output other contents." \

    agent(prompt)

    explaination_confidence = {}

    for inv in invariants:
        explaination_confidence[inv] = {}
        result = agent(inv)
        contents = result.message.get("content", [])
        if contents:
            response_text = "\n".join(item.get("text", "") for item in contents if isinstance(item, dict) and "text" in item)
            if response_text.strip():
                lines = list(filter(lambda x: len(x), response_text.strip().split('\n')))
                if len(lines) == 3:
                    explaination_confidence[inv]['explanation'] = lines[2].strip()
                    explaination_confidence[inv]['correctness_confidence'] = float(lines[0].strip())
                    explaination_confidence[inv]['criticalness_confidence'] = float(lines[1].strip())
                else:
                    print(f"Unexpected response format for invariant {inv}: {response_text}")
            else:
                print(f"No valid content returned for invariant {inv}.")
    print("\n\n=====Summarization given by the agent======")
    for inv, data in explaination_confidence.items():
        print(f"{inv}\nExplanation: {data.get('explanation', 'N/A')}\nCorrectness: {data.get('correctness_confidence', 'N/A')}\nCriticalness: {data.get('criticalness_confidence', 'N/A')}\n")
    print("===========================================")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Rank specifications based on their importance.')
    parser.add_argument('--top_k', type=int, default=20, help='Number of top specifications to return.')
    parser.add_argument('--model_id', type=str, default='us.anthropic.claude-3-7-sonnet-20250219-v1:0', help='Model ID to use for the agent.')
    parser.add_argument('--benchmarks', type=str, nargs='+', default=[], help='List of benchmarks to process.')
    parser.add_argument('--mode', type=str, choices=['monolithic', 'clustering', 'individual', 'oneshot'], default='monolithic', help='Ranking mode to use.')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximum number of retries for individual ranking.')
    parser.add_argument('--smoke-test', action='store_true', help='Run smoke test with all benchmarks and models.')
    parser.add_argument('--explain', action='store_true', help='Explain invariants for the given benchmark.')
    parser.add_argument('--summary-file', default='rank_summary_smoke.json', help='File to save the ranking summary.')
    parser.add_argument('--example', default='2PC', help='Example benchmark to use for one-shot ranking.')
    parser.add_argument('--percentage', action='store_true', help='Use percentage of specifications for top_k in one-shot ranking.')
    parser.add_argument('--chunk-size', type=int, default=10, help='Chunk size for ranking by score.')
    args = parser.parse_args()

    if args.smoke_test:
        print("Running smoke test...")
        def monolithic(model, benchmark, top_k=20, mode='monolithic', max_retries=3):
            return rank_and_check(model, benchmark, top_k, mode, max_retries)
        def oneshot(model, benchmark, top_k=20, mode='oneshot', max_retries=3):
            return one_shot_ranking(model, args.example, benchmark, top_k)
        if args.mode == 'individual':
            rank_by_score_all(args.example, benchmarks, chunk_size=args.chunk_size)
            exit(0)
        execfunc = {
            'monolithic': monolithic,
            'oneshot': oneshot
        }
        smoke_test(benchmarks + ['JournalLeaderElection', 'Kermit2PC'], execfunc[args.mode], percentage=args.percentage)
        exit(0)
    
    if args.explain:
        if not args.benchmarks:
            print("Please provide a benchmark to explain invariants.")
            exit(1)
        benchmark = args.benchmarks[0]
        if not check_prerequisites(benchmark):
            print(f"Skipping {benchmark} due to missing prerequisites.")
            exit(1)
        p_model = read_p_model(benchmark)
        agent = create_agent(args.model_id, p_model, args.top_k, with_task=False)
        with open(args.summary_file, 'r') as f:
            summary = json.load(f)
        benchmark_summaries = summary.get(args.model_id, {}).get(str(args.top_k), {})
        # print(summary[args.model_id])
        if benchmark not in benchmark_summaries:
            print(f"No summary found for benchmark: {benchmark} with model: {args.model_id} and top_k: {args.top_k}")
            exit(1)
        specs = benchmark_summaries.get(benchmark, {}).get('found_goals_raw', [])
        if not specs:
            print(f"No specifications found for benchmark: {benchmark}")
            exit(1)
        # result = rank_individual(agent, specs, args.top_k, args.max_retries)
        explain_invariants(benchmark, agent, specs)
        exit(0)

    top_k = args.top_k
    model_id = args.model_id
    benchmark = args.benchmarks if args.benchmarks else (benchmarks + ['JournalLeaderElection', 'Kermit2PC'])
    
    top_level_summary = {}
    for b in benchmark:
        try:
            if args.mode == 'monolithic':
                summary = rank_and_check(model_id, b, top_k, mode=args.mode, max_retries=args.max_retries)
            elif args.mode == 'oneshot':
                summary = one_shot_ranking(model_id, args.example, b, top_k)
            elif args.mode == 'individual':
                summary = rank_by_score(model_id, args.example, b, read_specs(b), top_k, chunk_size=args.chunk_size)
            else:
                raise ValueError(f"Unknown ranking mode: {args.mode}")
            top_level_summary[b] = summary
            with open(f'rank_summary_{args.mode}.json', 'w') as f:
                json.dump(top_level_summary, f, indent=4)
        except Exception as e:
            print(f"Exception occurred while processing benchmark {b}: {e}")
            import traceback
            traceback.print_exc()
            continue