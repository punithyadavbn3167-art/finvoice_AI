from backend.services.agent_router import route_query


test_cases = [
    # Finance: total expenses
    {
        "question": "How much did I spend?",
        "expected": "₹3,700.50",
    },
    {
        "question": "Show me my total expenses",
        "expected": "₹3,700.50",
    },

    # Finance: revenue
    {
        "question": "What is my total revenue?",
        "expected": "₹15,000.00",
    },
    {
        "question": "How much revenue did I earn?",
        "expected": "₹15,000.00",
    },

    # Finance: vendor-specific spending
    {
        "question": "How much did I spend on Amazon?",
        "expected": "₹2,500.00",
    },

    # Finance: receivables
    {
        "question": "How much am I waiting to receive?",
        "expected": "₹50,000.00",
    },

    # RAG: financial report
    {
        "question": "What does the financial report say?",
        "expected": "₹8,00,000",
    },

    # RAG: report revenue
    {
        "question": "According to the PDF, what was the revenue?",
        "expected": "₹15,00,000",
    },
    
    {
        "question": "How much did I spend at Amazon?",
        "expected": "₹2,500.00"
    },
    {
        "question": "What is the net balance?",
        "expected": "₹11,299.50"
    },
    {
        "question": "What profit is listed in the financial report?",
        "expected": "₹7,00,000"
    },
    {
        "question": "According to the PDF, what were the expenses?",
        "expected": "₹8,00,000"
    },
    
    {
        "question": "What was the revenue in the financial report for 2025?",
        "expected": "I could not find this information in the provided documents."
    },
    {
        "question": "What is my total spending on Microsoft?",
        "expected": "I could not find this information in the provided documents."
    },
]


def evaluate():

    passed = 0

    for test in test_cases:

        answer = route_query(test["question"])

        if test["expected"] in answer:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"

        print("=" * 60)
        print("Question:", test["question"])
        print("Expected:", test["expected"])
        print("Answer:", answer)
        print("Status:", status)

    total = len(test_cases)

    accuracy = (passed / total) * 100

    print("=" * 60)
    print(f"Evaluation Accuracy: {accuracy:.1f}%")
    print(f"Passed: {passed}/{total}")


if __name__ == "__main__":
    evaluate()