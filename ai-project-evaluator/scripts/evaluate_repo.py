import os
import sys
import shutil
import glob
import re
from pathlib import Path
import subprocess

def clone_repo(repo_url, target_dir):
    """Clones a git repository to the target directory."""
    try:
        subprocess.run(["git", "clone", repo_url, target_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def analyze_readme(repo_path):
    """Checks if README exists and estimates quality."""
    readme_files = glob.glob(os.path.join(repo_path, "README*"), recursive=False)
    if not readme_files: # Case insensitive check
        readme_files = [f for f in os.listdir(repo_path) if f.lower().startswith("readme")]
        if readme_files:
            readme_path = os.path.join(repo_path, readme_files[0])
        else:
            return "Missing", 0
    else:
        readme_path = readme_files[0]

    with open(readme_path, 'r', errors='ignore') as f:
        content = f.read()
    
    length = len(content)
    score = min(5, length // 500) # Simple heuristic: 1 point per 500 chars, max 5
    return "Present", score

def analyze_architecture(repo_path):
    """Analyzes file structure and languages."""
    languages = set()
    file_count = 0
    structure = []
    
    for root, dirs, files in os.walk(repo_path):
        if ".git" in dirs:
            dirs.remove(".git")
        
        level = root.replace(repo_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        structure.append('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        
        for f in files:
            file_count += 1
            ext = os.path.splitext(f)[1].lower()
            if ext in ['.py']: languages.add('Python')
            elif ext in ['.js', '.ts', '.jsx', '.tsx']: languages.add('JavaScript/TypeScript')
            elif ext in ['.java']: languages.add('Java')
            elif ext in ['.go']: languages.add('Go')
            elif ext in ['.rs']: languages.add('Rust')
            
            if file_count < 20: # Limit output
                structure.append('{}{}'.format(subindent, f))

    return list(languages), file_count, "\n".join(structure[:20])

def analyze_ai_usage(repo_path):
    """Checks for AI/ML libraries."""
    ai_keywords = [
        "openai", "langchain", "anthropic", "huggingface", "pytorch", "tensorflow", 
        "transformers", "llama", "deepseek", "gemini", "vertexai", "pinecone", "chromadb"
    ]
    detected_libs = set()
    
    # Check requirements.txt
    req_files = glob.glob(os.path.join(repo_path, "**", "requirements.txt"), recursive=True)
    for req_file in req_files:
        with open(req_file, 'r', errors='ignore') as f:
            content = f.read().lower()
            for kw in ai_keywords:
                if kw in content:
                    detected_libs.add(kw)

    # Check package.json
    package_files = glob.glob(os.path.join(repo_path, "**", "package.json"), recursive=True)
    for pkg_file in package_files:
        with open(pkg_file, 'r', errors='ignore') as f:
            content = f.read().lower()
            for kw in ai_keywords:
                if kw in content:
                    detected_libs.add(kw)
    
    return list(detected_libs)

def rate_prompts(repo_path):
    """Looks for prompt files and rates them."""
    prompt_score = 0
    prompt_files = []
    
    # Heuristic: look for files with 'prompt' in name or content
    for root, _, files in os.walk(repo_path):
        for file in files:
            if "prompt" in file.lower() or file.endswith(".txt") or file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read()
                        # Keywords for prompt engineering
                        if "system message" in content.lower() or "you are a" in content.lower() or "{{user}}" in content:
                            prompt_files.append(file)
                            # Basic rating: checks for clarity, constraints, examples
                            if "example" in content.lower() or "few-shot" in content.lower():
                                prompt_score += 2
                            if "do not" in content.lower() or "constraint" in content.lower():
                                prompt_score += 1
                            if len(content) > 100:
                                prompt_score += 1
                except:
                    pass
    
    final_score = min(5, prompt_score) if prompt_files else 0
    return final_score, prompt_files

def generate_report(repo_url, readme_status, readme_score, languages, file_count, ai_libs, prompt_score, structure):
    report = [
        f"# Project Evaluation Report for {repo_url}",
        "",
        "## Summary",
        f"- **Files**: {file_count}",
        f"- **Languages**: {', '.join(languages) if languages else 'Unknown'}",
        f"- **AI Libraries**: {', '.join(ai_libs) if ai_libs else 'None Detected'}",
        "",
        "## Ratings",
        f"- **Readme Quality**: {readme_score}/5 ({readme_status})",
        f"- **Prompt Engineering**: {prompt_score}/5",
        "",
        "## Architecture Overview",
        "```",
        structure,
        "..." if file_count > 20 else "",
        "```",
        "",
        "## AI Integration Check",
        "Project uses the following AI components:" if ai_libs else "No specific AI libraries found in dependency files.",
        *[f"- {lib}" for lib in ai_libs],
        "",
        "## Recommendation",
        "**APPROVED**" if (readme_score >= 3 and ai_libs) else "**NEEDS IMPROVEMENT**"
    ]
    
    if readme_score < 3:
        report.append("- Improve documentation/README.")
    if not ai_libs:
        report.append("- No AI dependencies found. Ensure AI integration is documented.")

    return "\n".join(report)

def main():
    if len(sys.argv) < 2:
        print("Usage: python evaluate_repo.py <repo_url> <output_file>")
        sys.exit(1)

    repo_url = sys.argv[1]
    output_file = sys.argv[2]
    temp_dir = "temp_repo_eval"
    
    # Cleanup prev run
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    print(f"Cloning {repo_url}...")
    if not clone_repo(repo_url, temp_dir):
        print("Failed to clone repository.")
        with open(output_file, "w") as f:
            f.write("Error: Failed to clone repository. Please check the URL.")
        return

    print("Analyzing...")
    readme_status, readme_score = analyze_readme(temp_dir)
    languages, file_count, structure = analyze_architecture(temp_dir)
    ai_libs = analyze_ai_usage(temp_dir)
    prompt_score, _ = rate_prompts(temp_dir)
    
    report = generate_report(repo_url, readme_status, readme_score, languages, file_count, ai_libs, prompt_score, structure)
    
    with open(output_file, "w") as f:
        f.write(report)
    
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    print(f"Report generated at {output_file}")

if __name__ == "__main__":
    main()
