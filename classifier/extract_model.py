#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import os
from typing import List, Dict, Optional, Set, Tuple
import logging
import sys

# 设置编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extract_model.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

VIDEO_ID_MAP = {
    "5DMuZEyU0Bg": ("KR2201W-4",      "manual"),
    "PTPRdGR7i2Y": ("RX480E",          "manual"),
    "lc3okJFk8lQ": ("FLCW-220V",       "manual"),
    "vbvFo_bG5b0": ("off_topic",       "auto_label"),
    "kr3RJoQmPvw": ("RX480E",          "manual"),
    "oSXfnkPHqoM": ("unclassified",    "unclassified"),
    "88uJ4nZVXTQ": ("KR2302",          "manual"),
    "HpPFJrSowDM": ("KR2201-4",        "manual"),
    "f0U9hoDz7lk": ("off_topic",       "auto_label"),
    "55W2CJUY1_k": ("KR1204",          "manual"),
    "Yxi-c3RG_4w": ("off_topic",       "auto_label"),
    "SRovqx89kJA": ("QA-R-011",        "manual"),
    "nA5qkfHKIco": ("unclassified",    "unclassified"),
    "h75XUOtdWRk": ("off_topic",       "auto_label"),
    "G05MCtylnZI": ("KR0548-1CH",      "manual"),
    "1Y6ipVZC9Ak": ("off_topic",       "auto_label"),
    "ljcjwBDyGsk": ("factory_content", "auto_label"),
    "lX2E2acxC6k": ("FLCW-220V",       "manual"),
    "WzMXEl4QKWE": ("off_topic",       "auto_label"),
    "W4-Do1tRaRE": ("unclassified",    "unclassified"),
    "saxzjPmtCM0": ("off_topic",       "auto_label"),
    "QmZSscz2wTc": ("unclassified",    "unclassified"),
    "lT5sMgPBjuU": ("unclassified",    "unclassified"),
    "1HksMUT8-_s": ("off_topic",       "auto_label"),
    "EIE0RMUKqiA": ("FLCW-220V",       "manual"),
    "zLfINct35x0": ("factory_content", "auto_label"),
    "AtIcWDfnPss": ("off_topic",       "auto_label"),
    "LUNNkMpFGLM": ("factory_content", "auto_label"),
    "yBN_w97g8Sw": ("off_topic",       "auto_label"),
    "N4HAYg2zIS4": ("factory_content", "auto_label"),
    "YQMpnhOEelc": ("factory_content", "auto_label"),
    "q6wiiptRDSQ": ("KR0548-1CH",      "manual"),
    "37JRtU8dWjY": ("FLCW-220V",       "manual"),
    "7uA6aox-cII": ("FLCW-220V",       "manual"),
    "1yyDrsb8iRI": ("off_topic",       "auto_label"),
    "1zCi6rJZFeE": ("off_topic",       "auto_label"),
    "vWdfIAUZZFk": ("KR2201-4",        "manual"),
    "-ZCKU0aK5SM": ("KR1204B",         "manual"),
    "BflR0s89cE8": ("unclassified",    "unclassified"),
    "Eblp2hSXBdE": ("off_topic",       "auto_label"),
    # ── 多型号修正：只保留正确的单一型号 ──
    "SnfOec3FBUw": ("FLCW-220V", "manual"),  # How to set ceiling fan light controller to quiet mode
    "wDB5Vl7iKYg": ("KR1204",    "manual"),  # How to use DC12V 4 Channel Remote Control Switch
    "9YbbvxmSoI4": ("KR1204",    "manual"),  # How to use : DC 12V Wireless RF 4-Channel
    "7IP1isvo5Sg": ("KR1204",    "manual"),  # How to use: 12v RF 4-Channel 433Mhz wireless
    "srkE5VFcg9g": ("KR1204",    "manual"),  # How to use QIACHIP DC 12V relay remote control switch Toggle Mode

    # ── KR1201A → KR1201 ──
    "7J1MdAHxLdc": ("KR2401FB,KR2401F", "manual"),
    "RsmifUNWlK0": ("KR1201", "manual"),
    "K17grRweDFc": ("KR1201", "manual"),
    "16ZhFlbFAYg": ("KR1201", "manual"),
    "3AWED-S6Hyk": ("KR1201", "manual"),
    "Ek68CFabr9c": ("KR1201", "manual"),
    "DLHtivdgIzM": ("KR1201", "manual"),
    "8wyGjrBSDaE": ("KR1201", "manual"),

    # ── KR1201A,KR1201C 共有 → KR1201（同时覆盖两个型号）──
    "l4dFZUkE3ZY": ("KR1201", "manual"),
    "ND1L7b8zpk4": ("KR1201", "manual"),
    "zyH0MqaYoZM": ("KR1201", "manual"),
    "o848jR8Pwaw": ("KR1201", "manual"),
}

def clean_description(text: str) -> str:
    """
    去除描述末尾的相关视频推荐区块，只保留正文。
    规则：按行扫描，遇到特定标志开头的行，从该行起截断。
    """
    if not text:
        return ""

    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        # 标志1：行首为 【
        if stripped.startswith('【'):
            break
        # 标志2：行首包含 youtube 链接
        if 'https://youtu.be/' in stripped or 'https://www.youtube.com/watch' in stripped:
            break
        # 标志3：行首为 Related / See also (不区分大小写)
        lower_line = stripped.lower()
        if lower_line.startswith('related') or lower_line.startswith('see also'):
            break

        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)

def normalize_text(text: str) -> str:
    """
    统一视频标题中常见的写法差异，提升关键词命中率。
    仅用于第三层 keyword 匹配，不影响前两层。
    """
    if not text:
        return ""
    t = text.lower()
    # DC/AC 与电压数字之间的空格去掉：DC 12V → DC12V
    t = re.sub(r'(dc|ac)\s+(\d)', r'\1\2', t)
    # 通道格式统一 → 1-ch
    t = re.sub(r'\b(\d)\s*-?\s*ch\b', r'\1-ch', t)
    t = re.sub(r'\b(\d)\s+channel\b', r'\1-ch', t)
    # RF+WiFi 各种写法统一
    t = re.sub(r'rf\s*[\+&]\s*wifi', 'rf+wifi', t)
    t = re.sub(r'wifi\s*[\+&]\s*rf', 'rf+wifi', t)
    # 频率格式统一
    t = re.sub(r'433\s*mhz', '433mhz', t)
    t = re.sub(r'868\s*mhz', '868mhz', t)
    t = re.sub(r'2\.4\s*g\b', '2.4g', t)
    return t

# ---------------------------------------------------------
# 第三层：KEYWORD_RULES 定义 (AND 逻辑 + 排除逻辑)
# ---------------------------------------------------------
KEYWORD_RULES = [

    # ══════════════════════════════════════════
    # FLC05 系列：Ceiling Fan Light（可区分，电压不同）
    # ══════════════════════════════════════════
    {
        "model": "FLC05-E110V",
        "require": ["ac90v-175v", "ceiling", "fan"],
        "exclude": ["220v", "265v"],
        "ambiguous": False,
        "ambiguous_with": []
    },
    {
        "model": "FLC05-E220V",
        "require": ["ac175v-265v", "ceiling", "fan"],
        "exclude": ["110v", "175v"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # KR0548 系列：DC7-48V + WIFI + Ewelink（三个可区分）
    # ══════════════════════════════════════════
    {
        "model": "KR0548-1CH",
        "require": ["wifi", "ewelink", "1-ch"],
        "exclude": ["ac110v", "ac220v", "matter", "zigbee", "2.4g"],
        "ambiguous": False,
        "ambiguous_with": []
    },
    {
        "model": "KR0548-2CH",
        "require": ["wifi", "ewelink", "2-ch"],
        "exclude": ["ac110v", "ac220v"],
        "ambiguous": False,
        "ambiguous_with": []
    },
    {
        "model": "KR0548-4CH",
        "require": ["wifi", "ewelink", "4-ch"],
        "exclude": ["ac110v", "ac220v"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # KR1201 系列：DC12V + 433MHz + 1-CH（无法区分 A/C）
    # ══════════════════════════════════════════
    {
        "model": "KR1201A",
        "require": ["dc12v", "433mhz", "1-ch"],
        "exclude": ["wifi", "motor", "4-ch", "2-ch"],
        "ambiguous": True,
        "ambiguous_with": ["KR1201C"]
    },
    {
        "model": "KR1201C",
        "require": ["dc12v", "433mhz", "1-ch"],
        "exclude": ["wifi", "motor", "4-ch", "2-ch"],
        "ambiguous": True,
        "ambiguous_with": ["KR1201A"]
    },

    # ══════════════════════════════════════════
    # KR1202 系列：Motor（可区分，电压不同）
    # ══════════════════════════════════════════
    {
        "model": "KR1202-30R",
        "require": ["dc5v-30v", "motor"],
        "exclude": ["220v", "110v"],
        "ambiguous": False,
        "ambiguous_with": []
    },
    {
        "model": "KR1202-V05",
        "require": ["dc5v-60v", "motor"],
        "exclude": ["220v", "110v"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # KR1204 系列：DC12V + 4-CH（可区分，电压不同）
    # ══════════════════════════════════════════
    {
        "model": "KR1204",
        "require": ["dc12v", "4-ch", "relay"],
        "exclude": ["wifi", "motor"],
        "ambiguous": False,
        "ambiguous_with": []
    },
    {
        "model": "KR1204B",
        "require": ["dc5v-80v", "4-ch"],
        "exclude": [],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # KR2201 大家族：AC110V + 433MHz + 1-CH（8个无法区分）
    # ══════════════════════════════════════════
    {
        "model": "KR2201-4",
        "require": ["ac110v", "433mhz", "1-ch"],
        "exclude": ["wifi", "tuya", "zigbee", "matter", "2.4g", "2-ch", "4-ch", "motor"],
        "ambiguous": True,
        "ambiguous_with": ["KR2201-COM", "KR2201B-4", "KR2201BL-4", "KR2201DA-4", "KR2201F-4", "KR2201G-4", "KR2201GS-4"]
    },
    {
        "model": "KR2201-COM",
        "require": ["ac110v", "433mhz", "1-ch"],
        "exclude": ["wifi", "tuya", "zigbee", "matter", "2.4g", "2-ch", "4-ch", "motor"],
        "ambiguous": True,
        "ambiguous_with": ["KR2201-4", "KR2201B-4", "KR2201BL-4", "KR2201DA-4", "KR2201F-4", "KR2201G-4", "KR2201GS-4"]
    },
    {
        "model": "KR2201B-4",
        "require": ["ac110v", "433mhz", "1-ch"],
        "exclude": ["wifi", "tuya", "zigbee", "matter", "2.4g", "2-ch", "4-ch", "motor"],
        "ambiguous": True,
        "ambiguous_with": ["KR2201-4", "KR2201-COM", "KR2201BL-4", "KR2201DA-4", "KR2201F-4", "KR2201G-4", "KR2201GS-4"]
    },
    {
        "model": "KR2201BL-4",
        "require": ["ac110v", "433mhz", "1-ch"],
        "exclude": ["wifi", "tuya", "zigbee", "matter", "2.4g", "2-ch", "4-ch", "motor"],
        "ambiguous": True,
        "ambiguous_with": ["KR2201-4", "KR2201-COM", "KR2201B-4", "KR2201DA-4", "KR2201F-4", "KR2201G-4", "KR2201GS-4"]
    },
    {
        "model": "KR2201DA-4",
        "require": ["ac110v", "433mhz", "1-ch"],
        "exclude": ["wifi", "tuya", "zigbee", "matter", "2.4g", "2-ch", "4-ch", "motor"],
        "ambiguous": True,
        "ambiguous_with": ["KR2201-4", "KR2201-COM", "KR2201B-4", "KR2201BL-4", "KR2201F-4", "KR2201G-4", "KR2201GS-4"]
    },
    {
        "model": "KR2201F-4",
        "require": ["ac110v", "433mhz", "1-ch"],
        "exclude": ["wifi", "tuya", "zigbee", "matter", "2.4g", "2-ch", "4-ch", "motor"],
        "ambiguous": True,
        "ambiguous_with": ["KR2201-4", "KR2201-COM", "KR2201B-4", "KR2201BL-4", "KR2201DA-4", "KR2201G-4", "KR2201GS-4"]
    },
    {
        "model": "KR2201G-4",
        "require": ["ac110v", "433mhz", "1-ch"],
        "exclude": ["wifi", "tuya", "zigbee", "matter", "2.4g", "2-ch", "4-ch", "motor"],
        "ambiguous": True,
        "ambiguous_with": ["KR2201-4", "KR2201-COM", "KR2201B-4", "KR2201BL-4", "KR2201DA-4", "KR2201F-4", "KR2201GS-4"]
    },
    {
        "model": "KR2201GS-4",
        "require": ["ac110v", "433mhz", "1-ch"],
        "exclude": ["wifi", "tuya", "zigbee", "matter", "2.4g", "2-ch", "4-ch", "motor"],
        "ambiguous": True,
        "ambiguous_with": ["KR2201-4", "KR2201-COM", "KR2201B-4", "KR2201BL-4", "KR2201DA-4", "KR2201F-4", "KR2201G-4"]
    },

    # ══════════════════════════════════════════
    # KR2201W-4：AC + RF+WIFI + Tuya（唯一）
    # ══════════════════════════════════════════
    {
        "model": "KR2201W-4",
        "require": ["rf+wifi", "tuya"],
        "exclude": ["zigbee", "matter"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # KR2201BY / KR2301-4：AC + WIFI + Ewelink（无法区分）
    # ══════════════════════════════════════════
    {
        "model": "KR2201BY",
        "require": ["ac110v", "wifi", "ewelink", "1-ch"],
        "exclude": ["rf+wifi", "matter", "zigbee", "2.4g", "motor"],
        "ambiguous": True,
        "ambiguous_with": ["KR2301-4"]
    },
    {
        "model": "KR2301-4",
        "require": ["ac110v", "wifi", "ewelink", "1-ch"],
        "exclude": ["rf+wifi", "matter", "zigbee", "2.4g", "motor"],
        "ambiguous": True,
        "ambiguous_with": ["KR2201BY"]
    },

    # ══════════════════════════════════════════
    # KR2301MT：Matter + WIFI + Ewelink（唯一）
    # ══════════════════════════════════════════
    {
        "model": "KR2301MT",
        "require": ["matter", "wifi", "ewelink"],
        "exclude": [],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # KR2202：AC + 2-CH + 433MHz（唯一）
    # ══════════════════════════════════════════
    {
        "model": "KR2202",
        "require": ["ac110v", "433mhz", "2-ch"],
        "exclude": ["wifi", "motor"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # KR2204：AC90V-250V + 4-CH（唯一）
    # ══════════════════════════════════════════
    {
        "model": "KR2204",
        "require": ["ac90v-250v", "4-ch"],
        "exclude": ["wifi"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # KR2303：ZigBee + Ewelink（唯一）
    # ══════════════════════════════════════════
    {
        "model": "KR2303",
        "require": ["zigbee", "ewelink"],
        "exclude": [],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # KR2305 / KR2201WB：AC + WIFI + Tuya（无法区分）
    # ══════════════════════════════════════════
    {
        "model": "KR2201WB",
        "require": ["ac110v", "wifi", "tuya", "1-ch"],
        "exclude": ["rf+wifi", "matter", "zigbee", "2.4g"],
        "ambiguous": True,
        "ambiguous_with": ["KR2305"]
    },
    {
        "model": "KR2305",
        "require": ["ac110v", "wifi", "tuya", "1-ch"],
        "exclude": ["rf+wifi", "matter", "zigbee", "2.4g"],
        "ambiguous": True,
        "ambiguous_with": ["KR2201WB"]
    },

    # ══════════════════════════════════════════
    # KR2306EW：2.4G + Ewelink（唯一）
    # ══════════════════════════════════════════
    {
        "model": "KR2306EW",
        "require": ["2.4g", "ewelink"],
        "exclude": [],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # KR2401F / KR2401FB / KR3001A：DC5V-60V + 1-CH（无法区分）
    # ══════════════════════════════════════════
    {
        "model": "KR2401F",
        "require": ["dc5v-60v", "433mhz", "1-ch"],
        "exclude": ["motor", "2-ch"],
        "ambiguous": True,
        "ambiguous_with": ["KR2401FB", "KR3001A"]
    },
    {
        "model": "KR2401FB",
        "require": ["dc5v-60v", "433mhz", "1-ch"],
        "exclude": ["motor", "2-ch"],
        "ambiguous": True,
        "ambiguous_with": ["KR2401F", "KR3001A"]
    },
    {
        "model": "KR3001A",
        "require": ["dc5v-60v", "433mhz", "1-ch"],
        "exclude": ["motor", "2-ch"],
        "ambiguous": True,
        "ambiguous_with": ["KR2401F", "KR2401FB"]
    },

    # ══════════════════════════════════════════
    # KR2402A：DC5V-60V + 2-CH（唯一，电机正反转）
    # ══════════════════════════════════════════
    {
        "model": "KR2402A",
        "require": ["dc5v-60v", "433mhz", "2-ch"],
        "exclude": ["motor"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # QA-R 系列：DC3.6V-24V + Lighting（无法区分 011/012/012V3）
    # ══════════════════════════════════════════
    {
        "model": "QA-R-011",
        "require": ["dc3.6v-24v", "lighting"],
        "exclude": [],
        "ambiguous": True,
        "ambiguous_with": ["QA-R-012", "QA-R-012V3"]
    },
    {
        "model": "QA-R-012",
        "require": ["dc3.6v-24v", "lighting"],
        "exclude": [],
        "ambiguous": True,
        "ambiguous_with": ["QA-R-011", "QA-R-012V3"]
    },
    {
        "model": "QA-R-012V3",
        "require": ["dc3.6v-24v", "lighting"],
        "exclude": [],
        "ambiguous": True,
        "ambiguous_with": ["QA-R-011", "QA-R-012"]
    },

    # ══════════════════════════════════════════
    # RX480E-868：868MHz（唯一）
    # ══════════════════════════════════════════
    {
        "model": "RX480E-868",
        "require": ["868mhz"],
        "exclude": [],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # RX480E：文档404，同系列推断（唯一）
    # ══════════════════════════════════════════
    {
        "model": "RX480E",
        "require": ["rx480e"],
        "exclude": ["1a", "4c", "868"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # RX480E-1A：DC2V-5V + Decoding（唯一）
    # ══════════════════════════════════════════
    {
        "model": "RX480E-1A",
        "require": ["dc2v-5v", "decoding"],
        "exclude": ["superheterodyne", "868mhz"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # RX480E-4C：DC3V-5V + Decoding（唯一）
    # ══════════════════════════════════════════
    {
        "model": "RX480E-4C",
        "require": ["dc3v-5v", "decoding"],
        "exclude": ["superheterodyne", "868mhz"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # RX18210A-4 / RX18211A-4 / RX217E-V01 / RX470-4
    # DC2V-5V + Superheterodyne（无法区分）
    # ══════════════════════════════════════════
    {
        "model": "RX18210A-4",
        "require": ["dc2v-5v", "superheterodyne"],
        "exclude": ["transmitter"],
        "ambiguous": True,
        "ambiguous_with": ["RX18211A-4", "RX217E-V01", "RX470-4"]
    },
    {
        "model": "RX18211A-4",
        "require": ["dc2v-5v", "superheterodyne"],
        "exclude": ["transmitter"],
        "ambiguous": True,
        "ambiguous_with": ["RX18210A-4", "RX217E-V01", "RX470-4"]
    },
    {
        "model": "RX217E-V01",
        "require": ["dc2v-5v", "superheterodyne"],
        "exclude": ["transmitter"],
        "ambiguous": True,
        "ambiguous_with": ["RX18210A-4", "RX18211A-4", "RX470-4"]
    },
    {
        "model": "RX470-4",
        "require": ["dc2v-5v", "superheterodyne"],
        "exclude": ["transmitter"],
        "ambiguous": True,
        "ambiguous_with": ["RX18210A-4", "RX18211A-4", "RX217E-V01"]
    },

    # ══════════════════════════════════════════
    # RX500-4：DC2V-5.5V + Superheterodyne（唯一，电压不同）
    # ══════════════════════════════════════════
    {
        "model": "RX500-4",
        "require": ["dc2v-5.5v", "superheterodyne"],
        "exclude": ["transmitter"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # TX118SA-4：Superheterodyne + Transmitter（唯一）
    # ══════════════════════════════════════════
    # ══════════════════════════════════════════
    # MTD12A-4 / TX118SA-4 / TX181-4：Transmitter/Motor
    # ══════════════════════════════════════════
    {
        "model": "MTD12A-4",
        "require": ["dc3v-16v", "micro", "motor"],
        "exclude": [],
        "ambiguous": False,
        "ambiguous_with": []
    },
    {
        "model": "TX118SA-4",
        "require": ["superheterodyne", "transmitter"],
        "exclude": [],
        "ambiguous": False,
        "ambiguous_with": []
    },
    {
        "model": "TX181-4",
        "require": ["power-on", "transmitter"],
        "exclude": [],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # WL 系列：Superheterodyne（唯一）
    # ══════════════════════════════════════════
    # ══════════════════════════════════════════
    # WL 系列：Superheterodyne（唯一）
    # ════──────────────────────────────────────
    {
        "model": "WL101-341",
        "require": ["dc3v-5v", "superheterodyne", "receiver"],
        "exclude": ["transmitter"],
        "ambiguous": False,
        "ambiguous_with": []
    },
    {
        "model": "WL102-341",
        "require": ["dc2v-3.6v", "superheterodyne", "transmitter"],
        "exclude": ["receiver"],
        "ambiguous": False,
        "ambiguous_with": []
    },

    # ══════════════════════════════════════════
    # 追加规则（提升标题命中率）
    # ══════════════════════════════════════════
    # KR2202 吊扇灯（标题常写 ceiling fan + 433mhz，不写 AC110V）
    {"model": "KR2202",    "require": ["ceiling fan", "433mhz"],
     "exclude": ["wifi", "tuya"],
     "ambiguous": False, "ambiguous_with": []},

    {"model": "KR2202",    "require": ["ceiling fan", "light", "rf"],
     "exclude": ["wifi", "tuya", "flcw"],
     "ambiguous": False, "ambiguous_with": []},

    # KR1201A（标题常写 12V 而非 DC12V）
    {"model": "KR1201A",   "require": ["12v", "1-ch", "relay"],
     "exclude": ["wifi", "motor", "220v", "110v", "4-ch", "2-ch"],
     "ambiguous": True, "ambiguous_with": ["KR1201C"]},

    # KR2402A 电机正反转
    {"model": "KR2402A",   "require": ["forward", "reverse", "motor"],
     "exclude": ["220v", "110v"],
     "ambiguous": False, "ambiguous_with": []},

    {"model": "KR2402A",   "require": ["linear actuator"],
     "exclude": [],
     "ambiguous": False, "ambiguous_with": []},

    # KR2401F 宽电压（标题常写 3.6V~24V 而非 DC5V-60V）
    {"model": "KR2401F", "require": ["3.6", "24v", "wireless"],
     "exclude": ["220v", "110v", "motor"],
     "ambiguous": True, "ambiguous_with": ["KR2401FB", "KR3001A"]},

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # A 组：克隆器/duplicator
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {"model": "duplicator", "require": ["duplicator"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "duplicator", "require": ["clone", "remote", "gate"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "duplicator", "require": ["cloning", "remote"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "duplicator", "require": ["copy", "remote", "433"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "duplicator", "require": ["came top"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "duplicator", "require": ["program", "remote", "garage"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # B 组：吊扇灯控制器（FLCW-220V）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {"model": "FLCW-220V", "require": ["ceiling fan", "wifi"],
     "exclude": ["flcw", "220v tuya"], "ambiguous": False, "ambiguous_with": []},
    {"model": "FLCW-220V", "require": ["ceiling fan", "wiring"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "FLCW-220V", "require": ["fan", "light", "beep"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "FLCW-220V", "require": ["ceiling fan", "smart life"],
     "exclude": ["flcw"], "ambiguous": False, "ambiguous_with": []},
    {"model": "FLCW-220V", "require": ["ceiling fan", "kit"],
     "exclude": ["flcw"], "ambiguous": False, "ambiguous_with": []},
    {"model": "FLCW-220V", "require": ["ceiling fan", "controller"],
     "exclude": ["flcw", "alexa"], "ambiguous": False, "ambiguous_with": []},
    {"model": "FLCW-220V", "require": ["3-in-1", "ceiling fan"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # C 组：智能插座/灯座（DT07）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {"model": "DT07", "require": ["lamp holder", "wireless"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "DT07", "require": ["light socket", "433mhz"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "DT07", "require": ["smart socket", "wireless"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "DT07", "require": ["ewelink", "lamp", "holder"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "DT07", "require": ["bulb base", "wireless"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # D 组：AC 2CH（KR2202）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {"model": "KR2202", "require": ["110v", "220v", "2ch"],
     "exclude": ["wifi", "motor"], "ambiguous": False, "ambiguous_with": []},
    {"model": "KR2202", "require": ["2ch receiver", "rf"],
     "exclude": ["dc", "motor"], "ambiguous": False, "ambiguous_with": []},

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # E 组：DC12V 1CH（KR1201A）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {"model": "KR1201A", "require": ["door lock", "relay"],
     "exclude": ["220v"], "ambiguous": True, "ambiguous_with": ["KR1201C"]},
    {"model": "KR1201A", "require": ["dc12v", "remote control switch"],
     "exclude": ["4ch", "wifi"], "ambiguous": True, "ambiguous_with": ["KR1201C"]},
    {"model": "KR1201A", "require": ["12v", "1 ch", "switch"],
     "exclude": ["220v", "4ch", "wifi"], "ambiguous": True, "ambiguous_with": ["KR1201C"]},
    {"model": "KR1201A", "require": ["12v", "load", "door lock"],
     "exclude": [], "ambiguous": True, "ambiguous_with": ["KR1201C"]},

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # F 组：AC 1CH 通用（KR2201-4）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {"model": "KR2201-4", "require": ["220v", "learning code", "relay"],
     "exclude": ["wifi", "2ch", "4ch"], "ambiguous": True,
     "ambiguous_with": ["KR2201-COM","KR2201B-4","KR2201BL-4","KR2201DA-4","KR2201F-4","KR2201G-4","KR2201GS-4"]},
    {"model": "KR2201-4", "require": ["220v", "wall panel", "receiver"],
     "exclude": ["wifi", "2ch", "4ch"], "ambiguous": True,
     "ambiguous_with": ["KR2201-COM","KR2201B-4","KR2201BL-4","KR2201DA-4","KR2201F-4","KR2201G-4","KR2201GS-4"]},
    {"model": "KR2201-4", "require": ["ac110v", "relay", "receiver"],
     "exclude": ["wifi", "2ch", "4ch", "zigbee", "matter"], "ambiguous": True,
     "ambiguous_with": ["KR2201-COM","KR2201B-4","KR2201BL-4","KR2201DA-4","KR2201F-4","KR2201G-4","KR2201GS-4"]},
    {"model": "KR2201-4", "require": ["85v", "250v", "relay"],
     "exclude": ["wifi", "2ch", "4ch"], "ambiguous": True,
     "ambiguous_with": ["KR2201-COM","KR2201B-4","KR2201BL-4","KR2201DA-4","KR2201F-4","KR2201G-4","KR2201GS-4"]},
    {"model": "KR2201-4", "require": ["433mhz", "220v", "light switch"],
     "exclude": ["wifi", "2ch", "4ch"], "ambiguous": True,
     "ambiguous_with": ["KR2201-COM","KR2201B-4","KR2201BL-4","KR2201DA-4","KR2201F-4","KR2201G-4","KR2201GS-4"]},
    {"model": "KR2201-4", "require": ["ac", "1-ch", "rf", "receiver"],
     "exclude": ["wifi", "dc", "2ch", "4ch"], "ambiguous": True,
     "ambiguous_with": ["KR2201-COM","KR2201B-4","KR2201BL-4","KR2201DA-4","KR2201F-4","KR2201G-4","KR2201GS-4"]},

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # G 组：电机控制（KR2402A）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {"model": "KR2402A", "require": ["4 channel", "motor"],
     "exclude": ["220v"], "ambiguous": False, "ambiguous_with": []},
    {"model": "KR2402A", "require": ["large motor", "wireless"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "KR2402A", "require": ["motor", "circuit modification"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "KR2402A", "require": ["capacitor", "motor", "12v"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # H 组：2.4G（KR2306EW）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {"model": "KR2306EW", "require": ["2.4ghz", "switch"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "KR2306EW", "require": ["2.4g", "moonlight"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},
    {"model": "KR2306EW", "require": ["2.4g", "86 panel"],
     "exclude": [], "ambiguous": False, "ambiguous_with": []},

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # J 组：mini 灯控（QA-R-011）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {"model": "QA-R-011", "require": ["night light", "remote"],
     "exclude": [], "ambiguous": True, "ambiguous_with": ["QA-R-012"]},
    {"model": "QA-R-011", "require": ["micro receiver", "light"],
     "exclude": [], "ambiguous": True, "ambiguous_with": ["QA-R-012"]},
    {"model": "QA-R-011", "require": ["mini", "receiver", "light"],
     "exclude": ["220v", "relay", "4ch"], "ambiguous": True, "ambiguous_with": ["QA-R-012"]},
]

# ---------------------------------------------------------
# 第二层：正则及排除定义
# ---------------------------------------------------------
# 必须大写的前缀
REGEX_PATTERN = r'\b(KR|KT|RX|TX|QA|DT|ZB|SM|KEY|MTD|FLC)[A-Z0-9]+(?:[-][A-Z0-9]+)*\b'

# 排除列表 (不区分大小写，存为大写方便检查)
EXCLUSIONS = {
    "DC12V", "AC220V", "USB5V", "DC24V", "DC5V", "DC48V", "AC110V",
    "ON", "OFF", "DIY", "RF", "USB", "WIFI", "SMART", "TUYA", "APP",
    "PCB", "AC", "DC", "LED", "KR221B"
}

def load_data(file_path: str) -> Dict:
    """加载 JSON 数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"加载文件 {file_path} 失败: {str(e)}")
        raise

def remove_substrings(models: List[str]) -> List[str]:
    """
    后处理过滤：如果短型号是长型号的前缀，则丢弃短型号，只保留长型号。
    示例：['KR1201', 'KR12010A'] -> 保留 ['KR12010A']
    """
    if not models:
        return []
    # 按长度从长到短排序
    models_sorted = sorted(list(set(models)), key=len, reverse=True)
    result = []
    for m in models_sorted:
        # 检查是否为任何已保留的长型号的前缀
        if not any(longer.startswith(m) and longer != m for longer in result):
            result.append(m)
    return sorted(result)

def tier1_exact_match(text: str, whitelist: List[str]) -> List[str]:
    """第一层：白名单精确匹配 (忽略大小写)"""
    if not text:
        return []

    matched = []
    text_lower = text.lower()
    sorted_whitelist = sorted(whitelist, key=len, reverse=True)

    temp_text = text_lower
    for model in sorted_whitelist:
        model_lower = model.lower()
        pattern = r'\b' + re.escape(model_lower) + r'\b'
        if re.search(pattern, temp_text):
            matched.append(model)
            temp_text = re.sub(pattern, ' ', temp_text)

    # 修复二：对返回结果做子串过滤
    return remove_substrings(matched)

def tier2_regex_match(text: str) -> List[str]:
    """第二层：正则表达式匹配 (前缀必须大写)"""
    if not text:
        return []

    full_matches = re.finditer(REGEX_PATTERN, text)

    results = []
    for m in full_matches:
        val = m.group()
        if val.upper() not in EXCLUSIONS:
            results.append(val)

    # 修复一：正则层增加前缀/子串过滤
    return remove_substrings(results)

def tier3_keyword_match(text: str, rules: List[Dict]) -> Tuple[List[str], List[int]]:
    """
    第三层：关键词映射匹配
    逻辑：require 全部命中 AND exclude 全部未命中 -> 匹配成功
    返回: (匹配到的型号列表, 匹配中的规则索引列表)
    """
    if not text:
        return [], []

    # 使用标准化后的文本进行匹配
    normalized_text = normalize_text(text)
    matched_models = []
    hit_rule_indices = []

    for idx, rule in enumerate(rules):
        # require 全部命中
        if all(kw in normalized_text for kw in rule["require"]):
            # exclude 全部未命中
            if not any(kw in normalized_text for kw in rule["exclude"]):
                matched_models.append(rule["model"])
                hit_rule_indices.append(idx)

    return list(set(matched_models)), hit_rule_indices

def auto_label_match(text: str) -> Optional[str]:
    """
    第四层：自动打标。
    识别工厂内容或无关主题。
    """
    t = text.lower()

    factory_keywords = [
        "what products have been tested", "what was packed",
        "what products are being packaged", "how was packed",
        "how was your product pack", "factory product packaging",
        "packing work", "soldering process", "soldering iron",
        "capacitor replacement", "resistor soldering",
        "relay replacement", "antenna soldering",
        "how to be produced", "quiet packing",
        "battle products", "from a drawing to a finished",
        "8 pin chip", "1-5 points",
        "tell you quietly",
        "he has 4 lights",
        "one module, one motor",
        "have you discovered the pattern",
        "how far can you control",
        "he for clients",
        "run 2 receiver",
        "answer questions with experiments",
        "incredible discovery",
        "very suitable for people",
        "what a strange",
        "speed control module",
        "remote control testing",
        "how simple the wireless",
        "compared with remote control",
        "white and round remote",
        "hand:learned",
        "man holding hammer",
        "swing control test",
        "pairing process of remote",
        "motor test after circuit",
        "more than just a box",
        "from concept to creation",
        "remote doorbell packing",
        "test：car alarm",
        "audible wiring process",
        "maintenance inspection",
        "maintenance：the controller",
        "replace the antenna",
        "preparation of soldering",
        "capacitor soldering on pcb",
        "soldering a resistor",
        "is there a possibility",
        "it can be controlled by phone",
        "everything can be remote controlled",
        "how to insert the module into the breadboard",
        "how to smart your home",
        "different pins determine",
        "remote control light system",
        "combination play",
        "nice! unified control",
        "remote control code value detector"
    ]

    offtopic_keywords = [
        "arduino uno", "bootloader", "atmega",
        "led breathing", "gimbal stabilizer",
        "uvc", "uv disinfection", "coospider",
        "sterilizer bag", "3d puzzle",
        "sport watch", "fitness tracker", "my office"
    ]

    if any(kw in t for kw in factory_keywords):
        return "factory_content"
    if any(kw in t for kw in offtopic_keywords):
        return "off_topic"
    return None

def process_video(video: Dict, whitelist: List[str]) -> Tuple[str, str, Optional[List[int]], str]:
    """
    整合完整四层流水线。
    采用严格的两轮分离匹配：先 title，再 cleaned description。
    """
    video_id = video.get('video_id', '')

    # 第零层：手动标注优先
    if video_id in VIDEO_ID_MAP:
        model, method = VIDEO_ID_MAP[video_id]
        return model, method, None, "manual"

    title = video.get('title', '')
    raw_desc = video.get('description', '')
    cleaned_desc = clean_description(raw_desc)

    # --- 第一轮：只用 title ---
    # 1. exact
    t1_matches = tier1_exact_match(title, whitelist)
    if t1_matches:
        return ",".join(t1_matches), "exact", None, "title"

    # 2. regex
    t2_matches = tier2_regex_match(title)
    if t2_matches:
        return ",".join(t2_matches), "regex", None, "title"

    # 3. keyword
    t3_matches, hit_indices = tier3_keyword_match(title, KEYWORD_RULES)
    if t3_matches:
        return ",".join(sorted(t3_matches)), "keyword", hit_indices, "title"


    # --- 第二轮：清洗后的 description (仅在 title 未命中时) ---
    # 1. exact
    t1_matches_desc = tier1_exact_match(cleaned_desc, whitelist)
    if t1_matches_desc:
        return ",".join(t1_matches_desc), "exact", None, "description"

    # 2. regex
    t2_matches_desc = tier2_regex_match(cleaned_desc)
    if t2_matches_desc:
        return ",".join(t2_matches_desc), "regex", None, "description"

    # 3. keyword
    t3_matches_desc, hit_indices_desc = tier3_keyword_match(cleaned_desc, KEYWORD_RULES)
    if t3_matches_desc:
        return ",".join(sorted(t3_matches_desc)), "keyword", hit_indices_desc, "description"


    # --- 后续层级 (使用合并后的文本) ---
    combined_text = f"{title} {cleaned_desc}"

    # --- 第四层：auto_label ---
    label = auto_label_match(combined_text)
    if label:
        return label, "auto_label", None, "description"

    return "unclassified", "unclassified", None, ""

def main():
    raw_path = 'data/raw/raw_videos.json'
    whitelist_path = 'data/raw/model_list.json'
    output_path = 'data/processed/videos_with_model.json'

    # 1. 加载数据
    raw_data = load_data(raw_path)
    whitelist_data = load_data(whitelist_path)
    whitelist = whitelist_data.get('models', [])

    logging.info(f"开始分类处理: {len(raw_data)} 条视频")

    processed_list = []
    stats = {
        "manual": 0, "exact": 0, "regex": 0, "keyword": 0,
        "auto_label": 0, "unclassified": 0
    }
    # 细分统计
    keyword_source_stats = {"title": 0, "description": 0}
    auto_label_stats = {"factory_content": 0, "off_topic": 0}

    rule_hits = [0] * len(KEYWORD_RULES)

    # 2. 遍历处理
    old_results = {}
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                old_results = {v['video_id']: v for v in old_data}
        except: pass

    for video in raw_data:
        model_str, method, hit_indices, source = process_video(video, whitelist)

        # 统计层级
        stats[method] += 1

        # 统计细分来源
        if method == "keyword":
            keyword_source_stats[source] += 1
            if hit_indices:
                for idx in hit_indices:
                    rule_hits[idx] += 1
        elif method == "auto_label":
            auto_label_stats[model_str] = auto_label_stats.get(model_str, 0) + 1

        # 创建新对象
        video_processed = video.copy()
        video_processed['model'] = model_str
        video_processed['match_method'] = method
        video_processed['match_source'] = source
        processed_list.append(video_processed)

    # 3. 保存结果
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_list, f, ensure_ascii=False, indent=2)

    # 4. 统计输出
    total = len(raw_data)
    print("\n" + "="*50)
    print("分类流水线任务完成！")
    print(f"总计视频: {total}")
    print("-" * 30)

    # 计算多型号对比
    multi_old = len([v for v in old_results.values() if ',' in v.get('model', '')])
    multi_new = len([v for v in processed_list if ',' in v.get('model', '')])

    print(f"第零层 [manual]          : {stats['manual']:3d} 条")
    print(f"第一层 [exact]           : {stats['exact']:3d} 条")
    print(f"第二层 [regex]           : {stats['regex']:3d} 条")
    print(f"第三层 [keyword]         : {stats['keyword']:3d} 条（title: {keyword_source_stats['title']} | description: {keyword_source_stats['description']}）")
    print(f"第四层 [auto_label]      : {stats['auto_label']:3d} 条（factory_content: {auto_label_stats.get('factory_content', 0)} | off_topic: {auto_label_stats.get('off_topic', 0)}）")
    print(f"未分类 [unclassified]    : {stats['unclassified']:3d} 条")
    print("-" * 30)
    print(f"多型号视频数量: {multi_old} (修改前) -> {multi_new} (修改后)")
    print("-" * 30)

    # 检查特定视频
    special_ids = {"qb8YAI0pAC4": "DT03", "NoNJqEA1yXU": "DT05", "9bKhAiMhafE": "DT07"}
    print("特定视频结果验证:")
    for v in processed_list:
        if v['video_id'] in special_ids:
            old_m = old_results.get(v['video_id'], {}).get('model', 'N/A')
            print(f"  [{special_ids[v['video_id']]}] {v['video_id']}: {old_m} -> {v['model']} ({v['match_source']})")

    print("="*50 + "\n")

if __name__ == "__main__":
    main()
