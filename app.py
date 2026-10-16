def get_customer_tags_html(customers):
    if not customers:
        return "<p style='color:#8A817C; font-size:15px;'>등록된 주요 고객사 정보가 없습니다.</p>"

    if not isinstance(customers, dict):
        return _legacy_customer_tags(list(customers))

    items = [(str(k).strip(), _parse_ratio(v)) for k, v in customers.items()]
    rated = [(k, v) for k, v in items if v is not None and v > 0 and not _is_etc(k)]

    if not rated:
        return _legacy_customer_tags([k for k, _ in items])

    rated.sort(key=lambda x: -x[1])
    top = rated[:CUSTOMER_TOP_N]

    rows = []
    if CUSTOMER_SHOW_ETC:
        total_all = sum(v for _, v in rated)
        base = total_all if total_all > 100.0 else 100.0
        for i, (name, val) in enumerate(top):
            bg, fg = CUSTOMER_PALETTE[i % len(CUSTOMER_PALETTE)]
            rows.append((name, val, val / base * 100.0, bg, fg, ""))
        etc_val = sum(v for _, v in rated[CUSTOMER_TOP_N:]) + max(0.0, 100.0 - total_all)
        if etc_val > 0.5:
            rows.append(("기타", etc_val, etc_val / base * 100.0, ETC_COLOR[0], ETC_COLOR[1], ""))
    else:
        base = sum(v for _, v in top) or 100.0
        for i, (name, val) in enumerate(top):
            bg, fg = CUSTOMER_PALETTE[i % len(CUSTOMER_PALETTE)]
            rows.append((name, val, val / base * 100.0, bg, fg, ""))

    segs = ""
    for name, val, w, bg, fg, tip in rows:
        disp = _short_name(name)
        cls = "cust-seg"
        if w >= 26:
            label = f"{disp} {_fmt_ratio(val)}%"
        elif w >= 13:
            label = f"{disp} {_fmt_ratio(val)}%"
            cls += " seg-md"
        elif w >= 3:
            label = f"{_fmt_ratio(val)}%"
            cls += " seg-sm"
        else:
            label = ""
        title = tip or f"{name} {_fmt_ratio(val)}%"
        
        # ✅ 확실한 해결책: 
        # Streamlit이 div나 span 안의 텍스트 색상을 덮어쓰지 못하도록
        # 텍스트 자체를 svg 안의 text 태그로 렌더링해버립니다.
        # 이렇게 하면 브라우저 렌더러 단에서 색상이 고정되어 절대 바뀌지 않습니다.
        
        if label:
            label_html = f"""
            <svg width="100%" height="100%" style="min-width: 50px;">
                <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{fg}" font-size="inherit" font-weight="900" font-family="inherit">
                    {label}
                </text>
            </svg>
            """
        else:
            label_html = ""

        segs += (
            f"<div class='{cls}' style='width:{w:.4f}%; background:{bg};' title='{title}'>"
            f"{label_html}"
            f"</div>"
        )

    return f"<div class='cust-box'><div class='cust-stack'>{segs}</div></div>"
