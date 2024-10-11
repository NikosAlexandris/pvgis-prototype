from rich import print
from typer.testing import CliRunner
from pvgisprototype.cli.cli import app

runner = CliRunner()

exclamation_mark = "\N{EXCLAMATION MARK}"
check_mark = "\N{CHECK MARK}"
x_mark = "\N{BALLOT SCRIPT X}"


def test_main_help():
    """Test if the CLI shows the main help message."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0  # Ensure the command ran successfully
    assert "PVGIS Command Line Interface" in result.output  # Check for expected output


def test_cli():
    total_commands = 0
    passed_tests = 0
    failed_tests = 0
    failed_commands = []

    # Iterate through all registered groups
    for group in app.registered_groups:
        result = runner.invoke(app, [group.name])
        
        total_commands += 1
        
        # Test the main command group
        if result.exit_code == 0:
            print(f"{check_mark} Group '{group.name}' passed.")
            passed_tests += 1
        else:
            print(f"{x_mark} Group '{group.name}' failed with exit code {result.exit_code}.")
            failed_tests += 1
            failed_commands.append(f"Group: {group.name}")

        # Retrieve and test subcommands
        if hasattr(group.typer_instance, 'registered_commands'):
            for command in group.typer_instance.registered_commands:
                if command.name:
                    total_commands += 1
                    subcommand = [group.name, command.name]
                    result = runner.invoke(app, subcommand)

                    if result.exit_code == 0:
                        print(f"  {check_mark} Subcommand '{' '.join(subcommand)}' passed.")
                        passed_tests += 1
                    else:
                        print(f"  {x_mark} Subcommand '{' '.join(subcommand)}' failed with exit code {result.exit_code}.")
                        failed_tests += 1
                        failed_commands.append(f"Subcommand: {' '.join(subcommand)}")

    print(f"\nTotal commands tested: {total_commands}")
    print(f"Passed tests: {passed_tests}")
    print(f"Failed tests: {failed_tests}")
    
    if failed_tests > 0:
        print(f"\nThe following commands failed:")
        for failed_command in failed_commands:
            print(f" - {failed_command}")
        assert False, f"{failed_tests} commands failed!"
    else:
        print("\nAll commands passed!")
