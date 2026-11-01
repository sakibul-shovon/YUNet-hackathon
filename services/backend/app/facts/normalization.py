import datetime
import re
from typing import Any

from pydantic import BaseModel, Field

# Bengali to ASCII digits translation map
BN_TO_EN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
EN_TO_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

BN_MONTHS = {
    "জানুয়ারি": 1,
    "জানুয়ারি": 1,
    "ফেব্রুয়ারি": 2,
    "ফেব্রুয়ারি": 2,
    "মার্চ": 3,
    "এপ্রিল": 4,
    "মে": 5,
    "জুন": 6,
    "জুলাই": 7,
    "আগস্ট": 8,
    "সেপ্টেম্বর": 9,
    "অক্টোবর": 10,
    "নভেম্বর": 11,
    "ডিসেম্বর": 12,
}

EN_MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}


def bengali_to_ascii_digits(text: str) -> str:
    """Translates Bengali digits (০-৯) to standard ASCII digits (0-9)."""
    return text.translate(BN_TO_EN_DIGITS)


def ascii_to_bengali_digits(text: str) -> str:
    """Translates ASCII digits (0-9) to Bengali digits (০-৯)."""
    return text.translate(EN_TO_BN_DIGITS)


# --- T05: Money Normalization (BDT minor units) ---


class MoneyValue(BaseModel):
    currency: str = "BDT"
    minor_units: int = Field(
        ..., description="Integer minor units (poisha), e.g. 550000 for 5,500.00 BDT"
    )
    original_text: str | None = None

    def to_bdt_float_str(self) -> str:
        """Formats to standard 2-decimal BDT string."""
        main_units = self.minor_units // 100
        poisha = abs(self.minor_units % 100)
        return f"{main_units:,}.{poisha:02d}"

    def to_bengali_display(self) -> str:
        """Formats with Bengali currency symbol and digits."""
        ascii_str = self.to_bdt_float_str()
        return f"৳{ascii_to_bengali_digits(ascii_str)}"


def normalize_bdt_money(val: Any, original_text: str | None = None) -> MoneyValue:
    """T05: Strictly normalizes money amounts to BDT integer minor units (poisha).

    Prevents IEEE 754 floating point imprecision.
    Handles Bengali digits, currency symbols (৳, Tk, BDT, Tk.), commas, and decimals.
    """
    if isinstance(val, MoneyValue):
        return val

    if isinstance(val, dict) and "minor_units" in val:
        return MoneyValue(
            currency=val.get("currency", "BDT"),
            minor_units=int(val["minor_units"]),
            original_text=original_text or val.get("original_text"),
        )

    orig = (
        original_text
        if original_text is not None
        else (str(val).strip() if val is not None else "")
    )

    # If original_text is provided and distinct from raw val, check if val was already minor units matching original_text
    if original_text and original_text != str(val):
        try:
            m_orig = normalize_bdt_money(original_text)
            if isinstance(val, int) and val == m_orig.minor_units:
                return m_orig
        except (ValueError, TypeError, AttributeError):
            m_orig = None

    raw_str = str(val).strip() if val is not None else ""

    if not raw_str:
        raise ValueError("Cannot normalize empty money value")

    # Step 1: Normalize digits to ASCII
    text = bengali_to_ascii_digits(raw_str)

    # Step 2: Strip currency signs and labels (৳, Tk, Tk., BDT, টাকা, etc.)
    text = re.sub(r"(?i)[৳]|bdt|tk\.?|টাকা", "", text).strip()

    # Step 3: Remove thousands commas (e.g. 5,500.50 -> 5500.50)
    text = text.replace(",", "").strip()

    # Step 4: Validate format: digits with optional decimal point
    match = re.search(r"^[-+]?(\d+)(?:\.(\d+))?$", text)
    if not match:
        raise ValueError(f"Invalid monetary string '{val}'")

    integer_part = int(match.group(1))
    decimal_part_str = match.group(2) or ""

    # Truncate or pad to exactly 2 decimal digits for poisha (cents)
    if len(decimal_part_str) == 0:
        poisha = 0
    elif len(decimal_part_str) == 1:
        poisha = int(decimal_part_str) * 10
    elif len(decimal_part_str) == 2:
        poisha = int(decimal_part_str)
    else:
        # Round 3+ decimals safely
        poisha = round(float("0." + decimal_part_str) * 100)

    is_negative = text.startswith("-")
    minor_units = (integer_part * 100) + poisha
    if is_negative:
        minor_units = -minor_units

    return MoneyValue(currency="BDT", minor_units=minor_units, original_text=orig)


# --- T06: Date Normalization (Date-only, ambiguity, relative & future dates) ---


class DateValue(BaseModel):
    date: str = Field(
        ..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="ISO 8601 Date string YYYY-MM-DD"
    )
    original_text: str | None = None
    is_relative: bool = False
    is_future: bool = False
    is_ambiguous: bool = False
    precision: str = "day"  # 'day', 'month', 'year'


def normalize_bd_date(val: str, reference_date: datetime.date | None = None) -> DateValue:
    """T06: Normalizes Bangladesh dates into strict calendar DATE (YYYY-MM-DD) with metadata.

    - Resolves DD/MM vs MM/DD ambiguity using BD convention (DD/MM/YYYY).
    - Preserves relative dates (yesterday, 3 days ago, গত পরশু).
    - Permits valid future promised delivery dates while flagging is_future=True.
    - Preserves date-only semantics without creating midnight UTC instant drift.
    """
    raw_str = val.strip()
    if not raw_str:
        raise ValueError("Cannot normalize empty date string")

    ref_date = reference_date or datetime.datetime.now(datetime.UTC).date()
    normalized_digits = bengali_to_ascii_digits(raw_str).strip()
    lower_text = raw_str.lower().strip()

    # 1. Relative dates check
    # Bengali relative patterns
    if lower_text in ("আজ", "আজকে", "today"):
        return DateValue(
            date=ref_date.isoformat(),
            original_text=raw_str,
            is_relative=True,
            is_future=False,
            is_ambiguous=False,
        )
    if lower_text in ("গতকাল", "yesterday"):
        d = ref_date - datetime.timedelta(days=1)
        return DateValue(
            date=d.isoformat(),
            original_text=raw_str,
            is_relative=True,
            is_future=False,
            is_ambiguous=False,
        )
    if lower_text in ("গত পরশু", "day before yesterday"):
        d = ref_date - datetime.timedelta(days=2)
        return DateValue(
            date=d.isoformat(),
            original_text=raw_str,
            is_relative=True,
            is_future=False,
            is_ambiguous=False,
        )
    if lower_text in ("আগামীকাল", "tomorrow"):
        d = ref_date + datetime.timedelta(days=1)
        return DateValue(
            date=d.isoformat(),
            original_text=raw_str,
            is_relative=True,
            is_future=True,
            is_ambiguous=False,
        )
    if lower_text in ("আগামী পরশু", "day after tomorrow"):
        d = ref_date + datetime.timedelta(days=2)
        return DateValue(
            date=d.isoformat(),
            original_text=raw_str,
            is_relative=True,
            is_future=True,
            is_ambiguous=False,
        )

    # Regex: N days ago / N দিন আগে
    m_days_ago = re.search(r"(\d+)\s*(?:days?\s*ago|দিন\s*আগে)", normalized_digits)
    if m_days_ago:
        n = int(m_days_ago.group(1))
        d = ref_date - datetime.timedelta(days=n)
        return DateValue(
            date=d.isoformat(),
            original_text=raw_str,
            is_relative=True,
            is_future=False,
            is_ambiguous=False,
        )

    # Regex: in N days / N দিন পর
    m_days_future = re.search(r"(?:in\s*)?(\d+)\s*(?:days?|দিন\s*পর)", normalized_digits)
    if m_days_future and ("ago" not in normalized_digits and "আগে" not in raw_str):
        n = int(m_days_future.group(1))
        d = ref_date + datetime.timedelta(days=n)
        return DateValue(
            date=d.isoformat(),
            original_text=raw_str,
            is_relative=True,
            is_future=True,
            is_ambiguous=False,
        )

    # 2. ISO format YYYY-MM-DD
    m_iso = re.match(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$", normalized_digits)
    if m_iso:
        y, m, d = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
        dt = datetime.date(y, m, d)
        return DateValue(
            date=dt.isoformat(),
            original_text=raw_str,
            is_relative=False,
            is_future=dt > ref_date,
            is_ambiguous=False,
        )

    # 3. Numeric DD/MM/YYYY or MM/DD/YYYY
    m_num = re.match(r"^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$", normalized_digits)
    if m_num:
        first, second, y = int(m_num.group(1)), int(m_num.group(2)), int(m_num.group(3))
        # In Bangladesh, the standard convention is DD/MM/YYYY
        if first > 12:
            # First must be day, second must be month
            day, month = first, second
            is_ambiguous = False
        elif second > 12:
            # Second is day, first is month (US format MM/DD/YYYY)
            month, day = first, second
            is_ambiguous = False
        else:
            # Both <= 12, ambiguous! Default to Bangladesh standard DD/MM/YYYY
            day, month = first, second
            is_ambiguous = True

        dt = datetime.date(y, month, day)
        return DateValue(
            date=dt.isoformat(),
            original_text=raw_str,
            is_relative=False,
            is_future=dt > ref_date,
            is_ambiguous=is_ambiguous,
        )

    # 4. Bengali textual date (e.g. ১৫ অক্টোবর ২০২৬ or 15 October 2026)
    for bn_month_name, m_num_val in BN_MONTHS.items():
        if bn_month_name in raw_str:
            # Extract day and year from normalized_digits
            numbers = re.findall(r"\d+", normalized_digits)
            if len(numbers) >= 2:
                day = int(numbers[0])
                year = int(numbers[1]) if len(numbers[1]) == 4 else int(numbers[0])
                if len(numbers[0]) == 4:
                    year, day = int(numbers[0]), int(numbers[1])
                dt = datetime.date(year, m_num_val, day)
                return DateValue(
                    date=dt.isoformat(),
                    original_text=raw_str,
                    is_relative=False,
                    is_future=dt > ref_date,
                    is_ambiguous=False,
                )

    # 5. English textual date (e.g. 15 October 2026 or Oct 15, 2026)
    for en_month_name, m_num_val in EN_MONTHS.items():
        if re.search(rf"\b{en_month_name}\b", lower_text):
            numbers = re.findall(r"\d+", normalized_digits)
            if len(numbers) >= 2:
                if len(numbers[0]) == 4:
                    year, day = int(numbers[0]), int(numbers[1])
                else:
                    day, year = int(numbers[0]), int(numbers[1])
                dt = datetime.date(year, m_num_val, day)
                return DateValue(
                    date=dt.isoformat(),
                    original_text=raw_str,
                    is_relative=False,
                    is_future=dt > ref_date,
                    is_ambiguous=False,
                )

    raise ValueError(f"Unrecognized date format: '{val}'")
