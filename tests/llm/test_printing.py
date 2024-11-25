from token_world.llm.printing import pretty_messages


def test_pretty_messages_single_message():
    messages = [{"sender": "Agent", "content": "Hello, world!", "tool_calls": []}]
    assert pretty_messages(messages) == "\033[94mAgent\033[0m: Hello, world!\n"


def test_pretty_messages_with_tool_calls():
    messages = [
        {
            "sender": "Agent",
            "content": "Processing...",
            "tool_calls": [
                {"function": {"name": "fetch_data", "arguments": '{"url": "http://example.com"}'}}
            ],
        }
    ]
    assert (
        pretty_messages(messages)
        == """\033[94mAgent\033[0m: Processing...
\033[95mfetch_data\033[0m("url": "http://example.com")
"""
    )


def test_pretty_messages_multiple_tool_calls():
    messages = [
        {
            "sender": "Agent",
            "content": "Processing...",
            "tool_calls": [
                {"function": {"name": "fetch_data", "arguments": '{"url": "http://example.com"}'}},
                {"function": {"name": "process_data", "arguments": '{"data": "sample"}'}},
            ],
        }
    ]
    assert (
        pretty_messages(messages)
        == """\033[94mAgent\033[0m: Processing...

\033[95mfetch_data\033[0m("url": "http://example.com")
\033[95mprocess_data\033[0m("data": "sample")
"""
    )


def test_pretty_messages_no_content():
    messages = [{"sender": "Agent", "content": "", "tool_calls": []}]
    assert pretty_messages(messages) == "\033[94mAgent\033[0m: \n"
