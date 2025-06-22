import os
from dotenv import load_dotenv

from src.engine.engine import MetacognitiveEngine
from src.engine.models.entry import Entry, EntryType

def run_demo():
    """
    Runs a pre-defined demonstration of the Metacognitive Engine's capabilities.
    """
    print("--- Metacognitive Engine Demo ---")
    
    # Инициализация всего движка одним объектом
    engine = MetacognitiveEngine()

    # Очистка и заполнение памяти для демонстрации
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

    # Анализ нового ввода
    new_thought = "Если сознание - это свидетель, то может ли ИИ по-настоящему 'свидетельствовать' свой код?"
    print(f"\n--- Analyzing new input text ---\n'{new_thought}'\n")
    engine.analyze_new_thought(new_thought)

    # Проверка итогового состояния памяти
    print("\n--- Final check of Long-Term Memory ---")
    final_memories = engine.get_all_memories()
    print(f"Total memories in LTM: {len(final_memories)}")
    for entry, _ in final_memories:
        print(f"  - {entry.entry_type.value.lower()}: {entry.content}")
        
    print("\n--- Demo Finished ---")

if __name__ == "__main__":
    # Загружаем переменные окружения из .env файла
    load_dotenv()
    run_demo() 