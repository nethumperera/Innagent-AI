# ════════════════════════════════════════════════════════════════
# InnAgent AI — OTA Rate Scraper
# Scrape competitor rates from Booking.com / Agoda
# ════════════════════════════════════════════════════════════════

import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import date
from backend.utils.logger import get_logger

logger = get_logger("ota_scraper")

# User agent to avoid blocks
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


async def scrape_booking_rates(
    hotel_url: str,
    check_in: date,
    check_out: date,
) -> List[dict]:
    """
    Scrape room rates from a Booking.com hotel page.
    Returns list of {room_type, rate_lkr, source}.
    Note: Booking.com actively blocks scraping. This is a best-effort
    implementation that may need proxy rotation for production.
    """
    if not hotel_url:
        return []

    rates = []
    try:
        params = {
            "checkin": check_in.isoformat(),
            "checkout": check_out.isoformat(),
            "group_adults": "2",
            "no_rooms": "1",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(hotel_url, params=params, headers=HEADERS, follow_redirects=True)

        if response.status_code != 200:
            logger.warning(f"Booking.com returned {response.status_code} for {hotel_url}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # Try to extract room rates from the page
        room_blocks = soup.select(".hprt-table tr.js-rt-block-row")
        for block in room_blocks:
            room_name_el = block.select_one(".hprt-roomtype-icon-link")
            price_el = block.select_one(".prco-valign-middle-helper")

            if room_name_el and price_el:
                room_name = room_name_el.get_text(strip=True)
                price_text = price_el.get_text(strip=True)
                # Extract numeric price
                price_num = "".join(c for c in price_text if c.isdigit())
                if price_num:
                    rates.append({
                        "room_type": room_name,
                        "rate_lkr": int(price_num),
                        "source": "booking.com",
                    })

        logger.info(f"Scraped {len(rates)} rates from Booking.com")

    except httpx.TimeoutException:
        logger.warning(f"Timeout scraping Booking.com: {hotel_url}")
    except Exception as e:
        logger.error(f"Error scraping Booking.com: {e}")

    return rates


async def scrape_agoda_rates(
    hotel_url: str,
    check_in: date,
    check_out: date,
) -> List[dict]:
    """
    Scrape room rates from an Agoda hotel page.
    Similar best-effort approach as Booking.com scraper.
    """
    if not hotel_url:
        return []

    rates = []
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(hotel_url, headers=HEADERS, follow_redirects=True)

        if response.status_code != 200:
            logger.warning(f"Agoda returned {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # Agoda uses dynamic rendering, so static scraping has limited success
        room_cards = soup.select("[data-selenium='RoomCard']")
        for card in room_cards:
            name_el = card.select_one("[data-selenium='RoomName']")
            price_el = card.select_one("[data-selenium='PriceDisplay']")

            if name_el and price_el:
                room_name = name_el.get_text(strip=True)
                price_text = price_el.get_text(strip=True)
                price_num = "".join(c for c in price_text if c.isdigit())
                if price_num:
                    rates.append({
                        "room_type": room_name,
                        "rate_lkr": int(price_num),
                        "source": "agoda",
                    })

        logger.info(f"Scraped {len(rates)} rates from Agoda")

    except httpx.TimeoutException:
        logger.warning(f"Timeout scraping Agoda: {hotel_url}")
    except Exception as e:
        logger.error(f"Error scraping Agoda: {e}")

    return rates


async def get_competitor_rates(
    hotel: dict,
    check_in: date,
    check_out: date,
) -> List[dict]:
    """
    Get competitor rates from all available OTA sources for a hotel.
    """
    all_rates = []

    booking_url = hotel.get("booking_com_url", "")
    if booking_url:
        rates = await scrape_booking_rates(booking_url, check_in, check_out)
        all_rates.extend(rates)

    agoda_url = hotel.get("agoda_url", "")
    if agoda_url:
        rates = await scrape_agoda_rates(agoda_url, check_in, check_out)
        all_rates.extend(rates)

    if not all_rates:
        logger.info("No competitor rates scraped — OTA URLs may be missing or blocked")

    return all_rates
