from todo_list import TodoList
import textwrap

def test_TodoList():
    # Create a new TodoList
    todo_list = TodoList()
    
    # Test default values
    assert todo_list.demo_link == "Ingen link enda"
    assert todo_list.chords_lyrics_link == "Ingen link enda"
    assert todo_list.todo_list == []
    assert todo_list.done_list == []
    
    # Test add_todo_item() method
    todo_list.add_todo_item("Task 1")
    assert todo_list.todo_list == ["Task 1"]
    
    # Test complete_todo_item() method
    todo_list.complete_todo_item(1)
    assert todo_list.todo_list == []
    assert todo_list.done_list == ["Task 1"]
    
    # Test undo_done_item() method
    todo_list.undo_done_item(1)
    assert todo_list.todo_list == ["Task 1"]
    assert todo_list.done_list == []
    
    # Test delete_completed_item() method
    todo_list.complete_todo_item(1)
    todo_list.delete_completed_item(1)
    assert todo_list.done_list == []
    
    # Test delete_todo_item() method
    todo_list.add_todo_item("Task 2")
    todo_list.delete_todo_item(1)
    assert todo_list.todo_list == []
    
    # Test __str__() method
    todo_list.demo_link = "https://www.example.com"
    todo_list.chords_lyrics_link = "https://www.example.com/chords"
    todo_list.add_todo_item("Task 1")
    todo_list.complete_todo_item(1)
    todo_list.add_todo_item("Task 2")
    todo_list.add_todo_item("Task 3")
    todo_list.complete_todo_item(2)
    expected_output = textwrap.dedent(f"""Link til demo: https://www.example.com
--------
Link til chords og lyrics: https://www.example.com/chords
--------
**Todo liste:**
--------
1. [ ] Task 2
--------
**Ferdige oppgaver:**
--------
1. [x] Task 1
2. [x] Task 3""")
    assert str(todo_list) == expected_output
