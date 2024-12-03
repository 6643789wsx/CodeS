import os
import ast
import pandas as pd

def analyze_code_distribution(paths):
    project_stats = {}
    
    for path in paths:
        stats = {
            'total_files': 0,
            'avg_functions_per_file': 0,
            'avg_lines_per_function': 0,
            'max_lines_in_function': 0,
            'min_lines_in_function': float('inf'),
            'no_external_deps': 0,
            'internal_deps_only': 0,
            'external_deps': 0
        }
        
        total_functions = 0
        total_lines_in_functions = 0
        function_lines = []
        
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    stats['total_files'] += 1
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                        total_functions += len(functions)
                        for func in functions:
                            lines = func.body[-1].lineno - func.body[0].lineno + 1
                            total_lines_in_functions += lines
                            function_lines.append(lines)
                            if lines > stats['max_lines_in_function']:
                                stats['max_lines_in_function'] = lines
                            if lines < stats['min_lines_in_function']:
                                stats['min_lines_in_function'] = lines
                            # Dependency analysis
                            calls = [node for node in ast.walk(func) if isinstance(node, ast.Call)]
                            internal_calls = [call for call in calls if isinstance(call.func, ast.Name)]
                            external_calls = [call for call in calls if not isinstance(call.func, ast.Name)]
                            if not calls:
                                stats['no_external_deps'] += 1
                            elif len(internal_calls) == len(calls):
                                stats['internal_deps_only'] += 1
                            else:
                                stats['external_deps'] += 1
        
        if stats['total_files'] > 0:
            stats['avg_functions_per_file'] = total_functions / stats['total_files']
        if total_functions > 0:
            stats['avg_lines_per_function'] = total_lines_in_functions / total_functions
            if stats['min_lines_in_function'] == float('inf'):
                stats['min_lines_in_function'] = 0
        
        project_stats[path] = stats
        print(f"Stats for {path}: {stats}")
    
    return project_stats

def save_stats_to_excel(stats, filename='analysis/result.xlsx'):
    df = pd.DataFrame.from_dict(stats, orient='index')
    df.to_excel(filename)

# Example usage
paths = [
    "/data/data_public/dtw_data/CodeS2/CodeS/validation/cleaned_repos/web.Monitor",
    "/data/data_public/dtw_data/CodeS2/CodeS/validation/cleaned_repos/libgen_to_txt", 
    "/data/data_public/dtw_data/CodeS2/CodeS/validation/cleaned_repos/pygraft",
]
project_stats = analyze_code_distribution(paths)
save_stats_to_excel(project_stats)


