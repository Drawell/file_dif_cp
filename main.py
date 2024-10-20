import os
import shutil


FROM_DIR = os.getenv("FROM")
TO_DIR = os.getenv("TO")


def list_files_and_dirs(path: str, sub_path='', depth=1) -> tuple[list[str], list[str]]:
    if depth > 10:
        print(f'Too deep: {path}')
        return [], []

    files = []
    dirs = []
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        rel_path = os.path.join(sub_path, item)
        if os.path.isdir(full_path) and '.' not in item:
            dirs.append(rel_path)
            sub_files, sub_dirs = list_files_and_dirs(full_path, item, depth + 1)
            files += sub_files
            dirs += sub_dirs
        elif ".mp3" in item:
            files.append(rel_path)

    return files, dirs


def diff_paths(from_paths: list[str], to_paths: list[str]) -> tuple[list[str], list[str]]:
    add = []
    for path in from_paths:
        to_full_path = os.path.join(TO_DIR, path)
        if not os.path.exists(to_full_path):
            add.append(path)

    remove = get_difference(to_paths, from_paths)
    return add, remove


def get_difference(base: list, to_remove: list):
    to_remove_set = set(to_remove)
    diff = [value for value in base if value not in to_remove_set]
    return diff


def sync_files(files_to_add: list[str], files_to_remove: list[str],
               dir_to_add: list[str], dir_to_remove: list[str]):
    remove_files(files_to_remove)
    remove_dirs(dir_to_remove)
    create_dirs(dir_to_add)
    copy_files(files_to_add)


def remove_files(path_list: list[str]):
    print("Removing files")
    count = len(path_list)
    for idx, path in enumerate(path_list):
        full_path = os.path.join(TO_DIR, path)
        if os.path.exists(full_path):
            print(f"   [{idx + 1}/{count}] REMOVED: {path}")
            os.remove(full_path)
        else:
            print(f"   [{idx + 1}/{count}] NOT FOUND: {path}")


def remove_dirs(path_list: list[str]):
    print("Removing dirs")
    count = len(path_list)
    for idx, path in enumerate(path_list):
        full_path = os.path.join(TO_DIR, path)
        if os.path.exists(full_path):
            print(f"   [{idx + 1}/{count}] REMOVED: {path}")
            os.removedirs(full_path)
        else:
            print(f"   [{idx + 1}/{count}] NOT FOUND: {path}")


def create_dirs(path_list: list[str]):
    print("Creating dirs")
    count = len(path_list)
    for idx, path in enumerate(path_list):
        to_path = os.path.join(TO_DIR, path)
        os.makedirs(to_path)
        print(f"   [{idx + 1}/{count}] DIR CREATED: {path}")


def copy_files(path_list: list[str]):
    print("Copying files")
    count = len(path_list)
    for idx, path in enumerate(path_list):
        from_path = os.path.join(FROM_DIR, path)
        to_path = os.path.join(TO_DIR, path)
        shutil.copyfile(from_path, to_path)
        print(f"   [{idx + 1}/{count}] COPIED: {path}")


def main():
    if not FROM_DIR or not TO_DIR:
        print("Determine FROM and TO env variables.")

    from_files, from_dirs = list_files_and_dirs(FROM_DIR)
    to_files, to_dirs = list_files_and_dirs(TO_DIR)

    print(f"Files in FROM={len(from_files)} and dirs={len(from_dirs)}")
    print(f"Files in TO={len(to_files)} and dirs={len(from_dirs)}")

    files_to_add, files_to_remove = diff_paths(from_files, to_files)
    dir_to_add, dir_to_remove = diff_paths(from_dirs, to_dirs)

    print(f"Files will be copied={len(files_to_add)}:")
    print("    ", end="")
    print("\n    ".join(files_to_add))

    print()

    print(f"Files will be removed={len(files_to_remove)}:")
    print("    ", end="")
    print("\n    ".join(files_to_remove))

    print()
    yes = input("Continue? [Y/N]:")
    if yes in ["Y", "y", "Н", "н"]:
        sync_files(files_to_add, files_to_remove, dir_to_add, dir_to_remove)
        print("Done")
    else:
        print("Bye")


if __name__ == '__main__':
    main()

