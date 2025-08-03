import sys
import pathlib
import runpy

def test_pipelineserver_init_adds_root_to_path(monkeypatch):
    """
    Tests that the pipelineserver's __init__.py correctly adds the project root
    to sys.path if it's missing.
    This is done by removing the path and then executing the __init__.py file directly.
    """
    # Path to the __init__.py file to be tested
    init_py_path = pathlib.Path(__file__).resolve().parent.parent / "__init__.py"
    
    # The project root path that __init__.py is supposed to add
    root_path = init_py_path.parents[2]
    root_path_str = str(root_path)

    # Create a new sys.path that does not contain the root path, resolving all paths
    # to handle potential differences in formatting (e.g., case on Windows).
    original_sys_path = list(sys.path)
    new_sys_path = [p for p in original_sys_path if str(pathlib.Path(p).resolve()) != str(root_path.resolve())]
    
    # Use monkeypatch to replace sys.path with our modified version for the test's duration
    monkeypatch.setattr(sys, 'path', new_sys_path)
    
    # Verify the path is truly gone from the patched sys.path
    assert not any(str(pathlib.Path(p).resolve()) == str(root_path.resolve()) for p in sys.path)

    # Execute the __init__.py file, which should add the path back
    runpy.run_path(str(init_py_path))

    # Verify that the path has now been added
    assert root_path_str in sys.path
