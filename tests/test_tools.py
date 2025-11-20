"""
Test tool execution
"""
from tools import get_global_registry


def test_tools():
    """Test all registered tools"""
    registry = get_global_registry()

    print("=" * 60)
    print("TOOL SYSTEM TEST")
    print("=" * 60)

    print("\n📦 Registered Tools:")
    for tool_name in registry.list_tools():
        print(f"  ✓ {tool_name}")

    print("\n🧮 Testing Calculator Tool:")
    result = registry.execute("CalculatorTool", expression="2 + 2")
    if result.success:
        print(f"  2 + 2 = {result.result}")
        assert result.result == 4, f"Expected 4, got {result.result}"
        print(f"  ✓ Basic calculation passed")
    else:
        print(f"  ✗ Calculator test failed: {result.error}")

    # Test percentage calculation
    result = registry.execute("CalculatorTool", expression="15% of 250")
    if result.success:
        print(f"  15% of 250 = {result.result}")
        assert result.result == 37.5, f"Expected 37.5, got {result.result}"
        print(f"  ✓ Percentage calculation passed")
    else:
        print(f"  ✗ Percentage test failed: {result.error}")

    print("\n📅 Testing Date Tool:")
    result = registry.execute("GetCurrentDateTool", format="date")
    if result.success:
        print(f"  Today: {result.result}")
        print(f"  ✓ Date tool passed")
    else:
        print(f"  ✗ Date test failed: {result.error}")

    print("\n📊 Testing Collection Stats Tool:")
    result = registry.execute("GetCollectionStatsTool")
    if result.success:
        print(f"  Collections found: {len(result.result)}")
        for coll_name, stats in result.result.items():
            if stats["status"] == "ok":
                print(f"    - {coll_name}: {stats['count']} documents")
            else:
                print(f"    - {coll_name}: ERROR")
        print(f"  ✓ Collection stats tool passed")
    else:
        print(f"  ✗ Collection stats test failed: {result.error}")

    print("\n🔍 Testing Search Tool:")
    result = registry.execute(
        "SearchVectorDBTool",
        query="What is RAG?",
        top_k=3
    )
    if result.success:
        print(f"  Found {len(result.result)} results")
        for i, r in enumerate(result.result, 1):
            print(f"    {i}. Source: {r['source']}")
            print(f"       Preview: {r['content'][:100]}...")
        print(f"  ✓ Search tool passed")
    else:
        print(f"  ⚠ Search test failed (this is OK if no documents indexed): {result.error}")

    print("\n📋 Testing Formatting Tools:")

    # Test table formatting
    test_data = [
        {"name": "Alice", "age": 30, "city": "NYC"},
        {"name": "Bob", "age": 25, "city": "SF"}
    ]
    result = registry.execute("FormatAsTableTool", data=test_data)
    if result.success:
        print("  Table format:")
        print(result.result)
        print(f"  ✓ Table formatting passed")
    else:
        print(f"  ✗ Table formatting failed: {result.error}")

    # Test bullet list formatting
    test_items = ["First item", "Second item", "Third item"]
    result = registry.execute("FormatAsBulletListTool", items=test_items)
    if result.success:
        print("\n  Bullet list format:")
        print(result.result)
        print(f"  ✓ Bullet list formatting passed")
    else:
        print(f"  ✗ Bullet list formatting failed: {result.error}")

    print("\n" + "=" * 60)
    print("✅ All tool tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_tools()
