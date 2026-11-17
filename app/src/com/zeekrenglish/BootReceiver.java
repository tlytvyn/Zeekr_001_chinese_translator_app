package com.zeekrenglish;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

/**
 * Re-applies the language chosen in this app after boot. Waits a few seconds so
 * it runs after zSupport's own boot receiver (which re-applies zSupport's saved
 * language). Does nothing if the user left language control to zSupport.
 */
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(final Context context, Intent intent) {
        if (!Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) return;
        final String lang = LangHelper.saved(context);
        if (lang == null) return;
        final PendingResult pr = goAsync();
        new Thread(new Runnable() {
            public void run() {
                try {
                    Thread.sleep(8000);
                    if (!lang.equals(LangHelper.current())) LangHelper.apply(lang);
                } catch (Throwable t) {
                    Log.e("ZeekrEnglish", "boot apply failed", t);
                } finally {
                    pr.finish();
                }
            }
        }).start();
    }
}
