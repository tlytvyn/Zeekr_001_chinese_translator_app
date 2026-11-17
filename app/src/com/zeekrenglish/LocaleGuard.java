package com.zeekrenglish;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;

/**
 * Some Zeekr component (profile/user center) re-applies Chinese on its own.
 * When the system language changes away from the language chosen in this app,
 * put it back. Rate-limited (max 3 times per 10 minutes) to never fight in a loop.
 */
public class LocaleGuard extends BroadcastReceiver {
    private static final String TAG = "ZeekrEnglish";

    @Override
    public void onReceive(final Context context, Intent intent) {
        if (!Intent.ACTION_LOCALE_CHANGED.equals(intent.getAction())) return;
        final String lang = LangHelper.saved(context);
        if (lang == null || lang.equals(LangHelper.current())) return;

        SharedPreferences p = context.getSharedPreferences("guard", Context.MODE_PRIVATE);
        long now = System.currentTimeMillis();
        long windowStart = p.getLong("window", 0);
        int count = p.getInt("count", 0);
        if (now - windowStart > 10 * 60 * 1000L) { windowStart = now; count = 0; }
        if (count >= 3) { Log.w(TAG, "LocaleGuard: rate limit reached, not reverting"); return; }
        p.edit().putLong("window", windowStart).putInt("count", count + 1).apply();

        final PendingResult pr = goAsync();
        new Thread(new Runnable() {
            public void run() {
                try {
                    Thread.sleep(3000);
                    if (!lang.equals(LangHelper.current())) {
                        Log.i(TAG, "LocaleGuard: language changed externally, restoring " + lang);
                        LangHelper.apply(lang);
                    }
                } catch (Throwable t) {
                    Log.e(TAG, "LocaleGuard failed", t);
                } finally {
                    pr.finish();
                }
            }
        }).start();
    }
}
