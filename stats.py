import os


def count_lines_of_code(directory):
    total_lines = 0
    for root, _, files in os.walk(directory):
        if str(root).__contains__(".venv"):
            continue
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    print(f"{file_path}: {len(lines)} lines")
    return total_lines


if __name__ == "__main__":
    project_directory = os.path.dirname(os.path.abspath(__file__))
    total_lines = count_lines_of_code(project_directory)
    print(f"Total lines of code: {total_lines}")