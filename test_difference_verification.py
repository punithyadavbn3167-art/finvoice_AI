
import re


def verify_difference(answer: str, expected_difference: float) -> bool:
    # Match the amount specifically on the "Difference:" line.
    match = re.search(
        r"^\s*Difference:\s*₹\s*([\d,]+(?:\.\d{2})?)\s*$",
        answer,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    if not match:
        return False

    actual_difference = float(match.group(1).replace(",", ""))

    return abs(actual_difference - expected_difference) < 0.005


def test_correct_difference_is_accepted():
    answer = (
        "Current expenses: ₹3,700.50\n"
        "Report expenses: ₹800,000.00\n"
        "Difference: ₹796,299.50"
    )
    assert verify_difference(answer, 796299.50)


def test_incorrect_difference_is_rejected():
    answer = (
        "Current expenses: ₹3,700.50\n"
        "Report expenses: ₹800,000.00\n"
        "Difference: ₹796,399.50"
    )
    assert not verify_difference(answer, 796299.50)


def test_wrong_difference_is_rejected_even_if_correct_amount_appears_elsewhere():
    answer = (
        "Current expenses: ₹3,700.50\n"
        "Report expenses: ₹800,000.00\n"
        "Difference: ₹796,399.50\n"
        "Expected difference: ₹796,299.50"
    )
    assert not verify_difference(answer, 796299.50)