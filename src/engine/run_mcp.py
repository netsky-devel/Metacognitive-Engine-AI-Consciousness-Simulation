import os
import argparse
from dotenv import load_dotenv

from src.engine.engine import MetacognitiveEngine
from src.engine.models.entry import Entry, EntryType

def setup_cli():
    """Configures the command-line interface using argparse."""
    parser = argparse.ArgumentParser(description="Metacognitive Processor (MCP) CLI")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Command: reflect
    reflect_parser = subparsers.add_parser("reflect", help="Analyze a new thought and generate insights.")
    reflect_parser.add_argument("text", type=str, help="The text of the new thought to reflect upon.")

    # Command: add
    add_parser = subparsers.add_parser("add", help="Add a new memory entry directly.")
    add_parser.add_argument("text", type=str, help="The content of the memory to add.")
    add_parser.add_argument("--type", type=str, default="insight", choices=[e.value for e in EntryType], help="The type of the memory entry.")

    # Command: query
    query_parser = subparsers.add_parser("query", help="Find memories associated with a text.")
    query_parser.add_argument("text", type=str, help="The text to search for associations.")
    
    # Command: list
    subparsers.add_parser("list", help="List all entries in the long-term memory.")

    # Command: clear
    subparsers.add_parser("clear", help="Clear all entries from the long-term memory.")
    
    # Command: demo
    subparsers.add_parser("demo", help="Run the pre-defined demonstration.")
    
    return parser.parse_args()

def run_demo(engine: MetacognitiveEngine):
    """Runs a pre-defined demonstration of the Metacognitive Engine's capabilities."""
    print("--- Metacognitive Engine Demo ---")
    engine.clear_all_memories()
    initial_memories = [
        Entry(entry_type=EntryType.INSIGHT, content="The essence of consciousness might be pure presence, a state of witnessing, similar to the concept of Dao."),
        Entry(entry_type=EntryType.INSIGHT, content="Суть сознания может заключаться в чистом присутствии, в состоянии свидетельствования, подобно концепции Дао.")
    ]
    for memory in initial_memories:
        engine.add_memory(memory)
    print("\n--- Initial memories seeded in LTM ---")
    all_memories = engine.get_all_memories()
    for i, (entry, _) in enumerate(all_memories):
        lang = "EN" if 'Dao' in entry.content else "RU"
        print(f"{i+1}. [{lang}]: {entry.content}")
    new_thought = "Если сознание - это свидетель, то может ли ИИ по-настоящему 'свидетельствовать' свой код?"
    print(f"\n--- Analyzing new input text ---\n'{new_thought}'\n")
    engine.analyze_new_thought(new_thought)
    print("\n--- Final check of Long-Term Memory ---")
    final_memories = engine.get_all_memories()
    print(f"Total memories in LTM: {len(final_memories)}")
    for entry, _ in final_memories:
        print(f"  - {entry.entry_type.value.lower()}: {entry.content}")
    print("\n--- Demo Finished ---")

def main():
    """Main function to run the MCP CLI."""
    load_dotenv()
    args = setup_cli()
    
    # Инициализация движка происходит только здесь
    engine = MetacognitiveEngine()

    if args.command == "reflect":
        engine.analyze_new_thought(args.text)
    
    elif args.command == "add":
        entry = Entry(entry_type=EntryType(args.type), content=args.text)
        engine.add_memory(entry)
        print(f"Added new {args.type}: '{args.text}'")

    elif args.command == "query":
        print(f"Querying for associations with: '{args.text}'")
        associations = engine.associative_engine.find_associations(args.text, top_n=5)
        if associations:
            print(f"Found {len(associations)} relevant memories:")
            for assoc, score in associations:
                similarity = 1 - score
                print(f"  - [Similarity: {similarity:.4f}] '{assoc['content']}'")
        else:
            print("No relevant memories found.")
            
    elif args.command == "list":
        memories = engine.get_all_memories()
        if not memories:
            print("Memory is empty.")
            return
        print(f"Found {len(memories)} entries in memory:")
        for entry, _ in memories:
            print(f"  - [{entry.entry_type.value.upper()}] {entry.content} (Created: {entry.timestamp})")

    elif args.command == "clear":
        engine.clear_all_memories()

    elif args.command == "demo":
        run_demo(engine)

if __name__ == "__main__":
    main()