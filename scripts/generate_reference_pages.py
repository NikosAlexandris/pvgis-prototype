"""Generate the code reference pages."""
from rich import print
from pathlib import Path

import mkdocs_gen_files


nav = mkdocs_gen_files.Nav()

package_root = "pvgisprototype"
src = Path(__file__).parent.parent / package_root
print(f':info: The `src` is set to [code]{src}[/code]')
skip_directories = {
    src / "algorithms" / "references",  # Example of a subdirectory path
    src / "api" / "surface",
    src / "plot",
    src / "web_api" / "plot",
    # Add other directories to skip as needed
}
print(f':info: Will skip the following directories : [reverse code]{skip_directories}[/reverse code]')

print(f'Processing identifiers :')
for path in sorted(src.rglob("*.py")):  
    
    if any(path.is_relative_to(skip_dir) for skip_dir in skip_directories):
        continue

    module_path = path.relative_to(src).with_suffix("")  
    doc_path = path.relative_to(src).with_suffix(".md")  
    full_doc_path = Path("reference", doc_path)  
    # print(f'Module path : {module_path}')
    # print(f'Doc path : {doc_path}')
    # print(f'Full doc path : {full_doc_path}')

    parts = [package_root] + list(module_path.parts)
    print(f'Module path part to assemble : {parts}')

    if parts[-1] == "__init__":  
        parts = parts[:-1]
    elif parts[-1] == "__main__":
        continue

    nav[parts] = doc_path.as_posix()  

    identifier = ".".join(parts)
    if identifier:  # Ensure identifier is not empty
        print(f'  [code]{identifier}[/code]')
        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            print("::: " + identifier, file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)  

# nav["mkdocs_autorefs", "references"] = "autorefs/references.md"
# nav["mkdocs_autorefs", "plugin"] = "autorefs/plugin.md"

# Generate a literate navigation file
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:  
    nav_file.writelines(nav.build_literate_nav())  
