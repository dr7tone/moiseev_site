"""Ветка feature-code: программный код лабораторной работы №5."""

def main():
    commands = [
        "git branch feature-code",
        "git switch feature-code",
        "git add lab5/branch_code.py",
        'git commit -m "Add branch code"',
        "git push -u origin feature-code",
    ]
    for command in commands:
        print(command)


if __name__ == "__main__":
    main()
