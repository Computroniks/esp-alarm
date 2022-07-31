# SPDX-FileCopyrightText: 2022 Matthew Nickson <mnickson@sidingsmedia.com>
# SPDX-License-Identifier: MIT

.PHONY = all upload

all: upload

upload: settings.txt .ampy
	ampy put settings.txt
	ampy put main.py
	ampy put alarm/
