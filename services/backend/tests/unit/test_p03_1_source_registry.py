from app.knowledge.source_registry import (
    OFFICIAL_HOST_ALLOWLIST,
    get_source_by_id,
    get_source_registry,
    is_private_or_restricted_ip,
    is_url_allowlisted,
)


def test_source_registry_integrity_and_no_fake_verified():
    """P03.1: Each URL labelled observed/unavailable/candidate; no inherited 'verified' flag from prose."""
    registry = get_source_registry()
    assert len(registry) >= 5

    valid_statuses = {"candidate", "observed", "unavailable"}

    for entry in registry:
        # Status MUST be one of candidate, observed, unavailable
        assert entry.status in valid_statuses, f"Entry {entry.id} has invalid status {entry.status}"
        # Invariant: Never allow an inherited or fabricated 'verified' flag on source candidates
        assert entry.status != "verified"

        # Must have bilingual titles and valid issuer
        assert entry.title_en and len(entry.title_en) > 3
        assert entry.title_bn and len(entry.title_bn) > 3
        assert entry.issuer and len(entry.issuer) > 3

        # Must pass URL allowlist
        allowed, reason = is_url_allowlisted(entry.official_url)
        assert allowed is True, f"Official URL for {entry.id} failed allowlist: {reason}"


def test_official_host_allowlist_validation():
    """Verifies that allowed official government portals pass and rogue domains fail."""
    # Official hosts
    assert is_url_allowlisted("https://ccms.dncrp.com/complaint/new")[0] is True
    assert is_url_allowlisted("http://bdlaws.minlaw.gov.bd/act-1014.html")[0] is True
    assert is_url_allowlisted("https://bb.org.bd/en/index.php/services/cipc_procedure")[0] is True
    assert is_url_allowlisted("http://dncrp.portal.gov.bd/")[0] is True
    assert is_url_allowlisted("http://subdomain.dncrp.gov.bd/page")[0] is True

    # Rogue or external domains
    allowed_bad1, _ = is_url_allowlisted("https://evil-consumer-complaints.com/steal")
    assert allowed_bad1 is False

    allowed_bad2, _ = is_url_allowlisted("https://dncrp.fake-portal.org")
    assert allowed_bad2 is False

    allowed_bad3, _ = is_url_allowlisted("ftp://bdlaws.minlaw.gov.bd/file")
    assert allowed_bad3 is False


def test_ssrf_and_private_ip_detection():
    """Verifies SSRF detection blocks loopback, private ranges, and cloud metadata."""
    assert is_private_or_restricted_ip("127.0.0.1") is True
    assert is_private_or_restricted_ip("10.0.0.5") is True
    assert is_private_or_restricted_ip("172.16.1.100") is True
    assert is_private_or_restricted_ip("192.168.1.1") is True
    assert is_private_or_restricted_ip("169.254.169.254") is True  # Metadata
    assert is_private_or_restricted_ip("::1") is True

    # Public safe IP
    assert is_private_or_restricted_ip("8.8.8.8") is False


def test_get_source_by_id_lookup():
    """Verifies exact lookup by source ID."""
    src = get_source_by_id("bd_crpa_2009")
    assert src is not None
    assert src.title_en == "Consumer Rights Protection Act, 2009 (Act No. 26 of 2009)"
    assert src.is_authoritative_for_penalties is True

    missing = get_source_by_id("non_existent_source_123")
    assert missing is None
