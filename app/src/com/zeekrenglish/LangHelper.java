package com.zeekrenglish;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.os.LocaleList;
import android.util.Log;

import java.lang.reflect.Method;
import java.util.Locale;

/**
 * Switches the system language (same mechanism zSupport uses, via the hidden
 * ActivityManager API; we run as the system uid). Ukrainian is applied as the
 * list [uk-UA, en-US] so anything not translated to Ukrainian falls back to
 * English instead of Chinese.
 */
public final class LangHelper {
    private static final String TAG = "ZeekrEnglish";
    static final String PREFS = "lang";
    static final String KEY = "managed_lang";   // "uk" | "en" | "zh" | absent = zSupport manages

    private LangHelper() { }

    static LocaleList listFor(String lang) {
        switch (lang) {
            case "uk": return new LocaleList(new Locale("uk"), Locale.ENGLISH);
            case "zh": return new LocaleList(Locale.CHINA);
            default:   return new LocaleList(Locale.ENGLISH);   // exactly "en", like zSupport
        }
    }

    static String current() {
        Locale l = LocaleList.getDefault().get(0);
        return l.getLanguage();
    }

    static String saved(Context c) {
        return c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(KEY, null);
    }

    static void save(Context c, String lang) {
        SharedPreferences.Editor e = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit();
        if (lang == null) e.remove(KEY); else e.putString(KEY, lang);
        e.apply();
    }

    /** Apply the language system-wide. Returns true on success. */
    static boolean apply(String lang) {
        try {
            Class<?> amn = Class.forName("android.app.ActivityManagerNative");
            Object am = amn.getMethod("getDefault").invoke(null);
            Configuration config = (Configuration) am.getClass().getMethod("getConfiguration").invoke(am);
            config.setLocales(listFor(lang));
            config.getClass().getField("userSetLocale").setBoolean(config, true);
            Method m;
            try {
                m = am.getClass().getMethod("updatePersistentConfiguration", Configuration.class);
            } catch (NoSuchMethodException e) {
                m = am.getClass().getMethod("updateConfiguration", Configuration.class);
            }
            m.invoke(am, config);
            Log.i(TAG, "Language set to " + lang);
            return true;
        } catch (Throwable t) {
            Log.e(TAG, "Language switch failed", t);
            return false;
        }
    }
}
