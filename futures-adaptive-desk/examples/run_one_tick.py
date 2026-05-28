# run_one_tick.py -- run a single (paper) desk tick and print the result.
# Showcase entry point; safe to run locally. No live broker calls.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from signal_engine import scan_signals
from confluence_engine import score
from risk_engine import RiskEngine

def main():
    risk = RiskEngine.from_defaults()
    signals = scan_signals(instrument="MES")            # representative scan
    for s in signals:
        s["confluence"] = score(s)                      # 0-100 / NO_TRADE
        decision = risk.evaluate(s)                     # gate stack
        print(f"{s['strategy']:>18}  score={s['confluence']:>3}  -> {decision}")
    if not signals:
        print("no setups this tick (expected outside active sessions)")

if __name__ == "__main__":
    main()
