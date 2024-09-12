from dataclasses import dataclass, field
import textwrap


@dataclass
class TodoList:
    demo_link: str = field(default="Ingen link enda")
    chords_lyrics_link: str = field(default="Ingen link enda")
    todo_list: list = field(default_factory=list)
    done_list: list = field(default_factory=list)

    @staticmethod
    def divider() -> str:
        return "--------\n"
    
    @classmethod
    def parse_message(cls, message: str) -> 'TodoList':
        sections = message.split(cls.divider())
        
        # Parse demo link
        demo_parts = sections[0].split(': ', 1)
        demo_link = demo_parts[1].strip() if len(demo_parts) > 1 else "Ingen link enda"
        
        # Parse chords and lyrics link
        chords_parts = sections[1].split(': ', 1)
        chords_lyrics_link = chords_parts[1].strip() if len(chords_parts) > 1 else "Ingen link enda"
        
        # Parse todo list
        todo_lines = sections[3].split('\n')  # Skip the "**Todo liste:**" line
        todo_list = [line.strip().split('- ', 1)[1] for line in todo_lines if line.strip() and line.strip() != "Ingen oppgaver enda"]
        
        # Parse done list
        done_lines = sections[5].split('\n')[1:]  # Skip the "**Ferdige oppgaver:**" line
        done_list = [line.strip().split('- ', 1)[1] for line in done_lines if line.strip() and line.strip() != "Ingen ferdige oppgaver enda"]

        return cls(
            demo_link=demo_link,
            chords_lyrics_link=chords_lyrics_link,
            todo_list=todo_list,
            done_list=done_list
        )
    
    def add_todo_item(self, item: str):
        self.todo_list.append(item)
    
    def complete_todo_item(self, idx: int):
        if not (0 < idx < len(self.todo_list) + 1):
            raise IndexError("Index out of range")
        idx -= 1
        item = self.todo_list.pop(idx)
        self.done_list.append(item)

    def undo_done_item(self, idx: int):
        if not (0 < idx < len(self.done_list) + 1):
            raise IndexError("Index out of range")
        idx -= 1
        item = self.done_list.pop(idx)
        self.todo_list.append(item)
    
    def delete_completed_item(self, idx: int):
        if not (0 < idx < len(self.done_list) + 1):
            raise IndexError("Index out of range")
        idx -= 1
        self.done_list.pop(idx)
    
    def delete_todo_item(self, idx: int):
        if not (0 < idx < len(self.todo_list) + 1):
            raise IndexError("Index out of range")
        idx -= 1
        self.todo_list.pop(idx)


    def __str__(self):
        todo_items = "\n".join([f"**[   ] {i+1}** - {item.strip()}" for i, item in enumerate(self.todo_list)]) if self.todo_list else "Ingen oppgaver enda"
        done_items = "\n".join([f"**[ x ] {i+1}** - {item.strip()}" for i, item in enumerate(self.done_list)]) if self.done_list else "Ingen ferdige oppgaver enda"

        return textwrap.dedent(f"""
Link til demo: {self.demo_link}
{self.divider()}
Link til chords og lyrics: {self.chords_lyrics_link}
{self.divider()}
**Todo liste:**
{self.divider()}
{todo_items}
{self.divider()}
**Ferdige oppgaver:**
{self.divider()}
{done_items}
""")

# if name main
if __name__ == "__main__":
    todo_list = TodoList()
    todo_list.demo_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    todo_list.todo_list.append("Oppgave 0")
    todo_list.done_list.append("Ferdig oppgave 0")

    a_list = todo_list.__str__()

    new_todo_list = TodoList.parse_message(a_list)
    new_todo_list.todo_list.append("Oppgave 1")
    print(new_todo_list)
    new_todo_list.todo_list.append("Oppgave 2")
    print(new_todo_list)
    