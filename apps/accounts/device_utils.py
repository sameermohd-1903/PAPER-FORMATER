from user_agents import parse


def get_device_information(request):

    user_agent = request.META.get(
        "HTTP_USER_AGENT",
        ""
    )

    ua = parse(user_agent)

    browser = (
        f"{ua.browser.family} "
        f"{ua.browser.version_string}"
    )

    operating_system = (
        f"{ua.os.family} "
        f"{ua.os.version_string}"
    )

    device_name = (
        ua.device.family
    )

    ip_address = (
        request.META.get(
            "REMOTE_ADDR"
        )
    )

    return {
        "browser": browser,
        "operating_system": operating_system,
        "device_name": device_name,
        "ip_address": ip_address,
    }