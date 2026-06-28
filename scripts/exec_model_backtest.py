import runpy,traceback
try:
    runpy.run_path('src/domain/evaluation/model_backtest.py', run_name='__main__')
    print('EXEC OK')
except Exception:
    traceback.print_exc()
