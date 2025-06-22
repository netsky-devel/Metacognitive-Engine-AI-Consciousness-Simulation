from src.engine import MetacognitiveEngine
from src.engine.models.entry import Entry, EntryType


def run_demo():
    """
    A demonstration of the ConsciousnessJournal.
    """
    print("--- Metacognitive Engine Demo ---")
    
    # 1. Инициализация движка
    engine = MetacognitiveEngine()

    # 2. Очистка старых воспоминаний для чистоты эксперимента
    engine.long_term_memory.clear_all_memories()

    # 3. Добавление "воспоминаний" на разных языках
    # Английское воспоминание
    dao_insight_en = Entry(
        content="The essence of consciousness might be pure presence, a state of witnessing, similar to the concept of Dao.",
        entry_type=EntryType.INSIGHT
    )
    engine.add_memory(dao_insight_en)
    
    # Русское воспоминание
    dao_insight_ru = Entry(
        content="Суть сознания может заключаться в чистом присутствии, в состоянии свидетельствования, подобно концепции Дао.",
        entry_type=EntryType.INSIGHT
    )
    engine.add_memory(dao_insight_ru)

    print("\n--- Initial memories seeded in LTM ---")
    print(f"1. [EN]: {dao_insight_en.content}")
    print(f"2. [RU]: {dao_insight_ru.content}")
    
    # 4. Анализ нового входящего текста на русском языке
    # Этот текст семантически близок к русскому воспоминанию
    new_russian_text = "Я размышлял сегодня о природе самосознания и моментах чистого бытия."
    
    print(f"\n--- Analyzing new input text ---\n'{new_russian_text}'")
    
    # 5. Запуск когнитивного цикла
    engine.cognitive_cycle(new_russian_text)

    print("\n--- Demo Finished ---")


if __name__ == "__main__":
    run_demo() 