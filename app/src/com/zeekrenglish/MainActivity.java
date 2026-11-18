package com.zeekrenglish;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageInfo;
import android.content.pm.PackageInstaller;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;

import java.io.InputStream;
import java.io.OutputStream;
import java.lang.reflect.Method;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/**
 * Zeekr English: installs and toggles text-only overlays (RRO) that add missing
 * English strings to Zeekr apps. The original apps are never modified.
 */
public class MainActivity extends Activity {
    private static final String TAG = "ZeekrEnglish";
    private static final String ACTION_RESULT = "com.zeekrenglish.INSTALL_RESULT";
    private static final int USER = 0;
    private static final int OVERLAY_VERSION = 112;

    /**
     * Language buttons: {code, button text}. "en" is the base layer (English overlays, always ON).
     * Every other code enables the overlay set com.zeekrenglish.<code>.* bundled in assets/ov/
     * (built by tools/build_overlays.py from LANGS there). Add a row here to add a language button.
     */
    private static final String[][] LANGS = {
            {"uk", "Українська"},
            {"en", "English"},
    };

    // overlay package, target package, label shown to the user
    private static final String[][] OVERLAYS = {
            {"com.zeekrenglish.lbl.mxplayer", "com.mxtech.videoplayer.ad", "App name: mxplayer"},
            {"com.zeekrenglish.lbl.pdfhiread", "pdf.reader.pdfviewer.pdfeditor", "App name: pdfhiread"},
            {"com.zeekrenglish.lbl.microg", "app.revanced.android.gms", "App name: microg"},
            {"com.zeekrenglish.lbl.langswitch", "com.geely.pma.settings.launage", "App name: langswitch"},
            {"com.zeekrenglish.lbl.iqiyi", "com.arcvideo.car.video", "App name: iqiyi"},
            {"com.zeekrenglish.lbl.bilibili", "com.bilibili.bilithings", "App name: bilibili"},
            {"com.zeekrenglish.lbl.thunderktv", "com.thunder.carplay", "App name: thunderktv"},
            {"com.zeekrenglish.ov.extsound", "com.mrbattery.exterioraudioplaydemo", "Exterior Sound"},
            {"com.zeekrenglish.lbl.btphone", "com.ecarx.btphone", "App name: btphone"},
            {"com.zeekrenglish.lbl.mycar", "com.ecarx.mycar", "App name: mycar"},
            {"com.zeekrenglish.lbl.gallery", "ecarx.gallery", "App name: gallery"},
            {"com.zeekrenglish.lbl.lightshow", "com.geely.pma.lightshow", "App name: lightshow"},
            {"com.zeekrenglish.lbl.multimedia", "com.ecarx.multimedia", "App name: multimedia"},
            {"com.zeekrenglish.lbl.membercenter", "ecarx.membercenter", "App name: membercenter"},
            {"com.zeekrenglish.lbl.usermanual", "com.ecarx.usermanual", "App name: usermanual"},
            {"com.zeekrenglish.lbl.dvr", "ecarx.camera.dvr", "App name: dvr"},
            {"com.zeekrenglish.lbl.gamepad", "com.zeekr.gamepad", "App name: gamepad"},
            {"com.zeekrenglish.lbl.dlnavideo", "com.zeekr.dlnavideo", "App name: dlnavideo"},
            {"com.zeekrenglish.lbl.speechsetting", "com.zeekr.speech.setting", "App name: speechsetting"},
            {"com.zeekrenglish.lbl.market", "com.zeekrlife.market", "App name: market"},
            {"com.zeekrenglish.lbl.extsound", "com.mrbattery.exterioraudioplaydemo", "App name: extsound"},
            {"com.zeekrenglish.lbl.manager", "com.zeekr.managerapplication", "App name: manager"},
            {"com.zeekrenglish.lbl.media", "com.zeekr.media", "App name: media"},
            {"com.zeekrenglish.ov.settings", "com.geely.pma.settings", "Vehicle Settings (Driving, Zeekr AD, Safety, Connectivity, Energy)"},
            {"com.zeekrenglish.ov.climate", "com.geely.pma.climate", "Climate"},
            {"com.zeekrenglish.ov.btphone", "com.ecarx.btphone", "Phone"},
            {"com.zeekrenglish.ov.sentry", "zeekr.bx.sentry", "Sentry mode"},
            {"com.zeekrenglish.ov.dvr", "ecarx.camera.dvr", "Camera / Dashcam"},
            {"com.zeekrenglish.ov.carlauncher3d", "com.zeekr.carlauncher3d", "3D car view (pet mode, rest mode, car wash)"},
            {"com.zeekrenglish.ov.launcher3", "ecarx.launcher3", "Home screen (cards, weather, app editor; replaces Russian)"},
            {"com.zeekrenglish.ov.systemui", "com.android.systemui", "Status bar, clock, calendar, volume"},
            {"com.zeekrenglish.ov.membercenter", "ecarx.membercenter", "User center & driving profiles"},
            {"com.zeekrenglish.ov.quickpanel", "ecarx.notificationcenterui", "Quick panel"},
            {"com.zeekrenglish.ov.housekeeper", "com.zeekr.housekeeper", "Housekeeper"},
            {"com.zeekrenglish.ov.market", "com.zeekrlife.market", "ZEEKR App Store"},
            {"com.zeekrenglish.ov.mycar", "com.ecarx.mycar", "My car (trips, energy, tire widgets)"},
            {"com.zeekrenglish.ov.speechsetting", "com.zeekr.speech.setting", "Voice assistant settings"},
            {"com.zeekrenglish.ov.upgrade", "ecarx.upgrade", "System updates (OTA)"},
            {"com.zeekrenglish.ov.autopilot", "com.zeekr.autopilot", "NZP / driver assistance pilot"},
            {"com.zeekrenglish.ov.dlnavideo", "com.zeekr.dlnavideo", "Video casting"},
            {"com.zeekrenglish.ov.modes", "com.geely.pma.bs.modes", "Scene modes (rest, camping, wash, pet)"},
            {"com.zeekrenglish.ov.manager", "com.zeekr.managerapplication", "Car Manager"},
            {"com.zeekrenglish.ov.usermanual", "com.ecarx.usermanual", "User manual"},
            {"com.zeekrenglish.ov.media", "com.zeekr.media", "ZEEKR Music (极享)"},
            {"com.zeekrenglish.ov.mediacenter", "com.zeekr.mediacenter", "Media center / Eva media replies"},
            {"com.zeekrenglish.ov.multimedia", "com.ecarx.multimedia", "Radio / USB / Bluetooth music"},
            {"com.zeekrenglish.ov.smartscene", "com.ecarx.smartscene", "Smart scenes"},
            {"com.zeekrenglish.ov.feedback", "com.zeekr.feedback", "Feedback"},
            {"com.zeekrenglish.ov.accountcenter", "com.ecarx.accountcenter", "Account center"},
            {"com.zeekrenglish.ov.profile", "com.ecarx.profile", "Profile"},
            {"com.zeekrenglish.ov.mediaswitch", "com.zeekr.mediaswitch", "Media switcher"},
            {"com.zeekrenglish.ov.lightshow", "com.geely.pma.lightshow", "Music Light Show"},
    };

    private final Handler ui = new Handler(Looper.getMainLooper());
    private TextView status;
    private TextView langState;
    private final Switch[] switches = new Switch[OVERLAYS.length];
    private final TextView[] states = new TextView[OVERLAYS.length];
    private volatile CountDownLatch latch;
    private volatile int lastStatus;
    private volatile String lastMessage;

    private final BroadcastReceiver resultReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context c, Intent i) {
            lastStatus = i.getIntExtra(PackageInstaller.EXTRA_STATUS, PackageInstaller.STATUS_FAILURE);
            lastMessage = i.getStringExtra(PackageInstaller.EXTRA_STATUS_MESSAGE);
            CountDownLatch l = latch;
            if (l != null) l.countDown();
        }
    };

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        registerReceiver(resultReceiver, new IntentFilter(ACTION_RESULT));
        setContentView(buildUi());
    }

    @Override
    protected void onDestroy() {
        unregisterReceiver(resultReceiver);
        super.onDestroy();
    }

    @Override
    protected void onResume() {
        super.onResume();
        refresh();
        refreshLang();
    }

    // ---------------------------------------------------------------- UI

    private View buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(60, 40, 60, 40);
        root.setBackgroundColor(Color.rgb(24, 26, 30));

        TextView title = text("Zeekr English  v" + version(), 40, Color.WHITE);
        root.addView(title);
        TextView sub = text("Adds missing English text to Zeekr apps. Original apps are not modified. "
                + "Language itself is still switched with zSupport.", 22, Color.rgb(170, 175, 185));
        sub.setPadding(0, 10, 0, 30);
        root.addView(sub);

        for (int i = 0; i < OVERLAYS.length; i++) {
            final int idx = i;
            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);
            row.setGravity(Gravity.CENTER_VERTICAL);
            row.setPadding(0, 14, 0, 14);

            LinearLayout col = new LinearLayout(this);
            col.setOrientation(LinearLayout.VERTICAL);
            col.addView(text(OVERLAYS[i][2], 28, Color.WHITE));
            states[i] = text("", 20, Color.rgb(150, 155, 165));
            col.addView(states[i]);
            row.addView(col, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

            Switch sw = new Switch(this);
            sw.setScaleX(1.5f);
            sw.setScaleY(1.5f);
            switches[i] = sw;
            row.addView(sw);
            root.addView(row);
        }

        TextView langTitle = text("Language / Мова / 语言", 28, Color.WHITE);
        langTitle.setPadding(0, 30, 0, 10);
        root.addView(langTitle);
        LinearLayout langs = new LinearLayout(this);
        langs.setOrientation(LinearLayout.HORIZONTAL);
        for (final String[] l : LANGS) {
            langs.addView(button(l[1], new View.OnClickListener() {
                public void onClick(View v) { chooseLanguage(l[0]); }
            }));
        }
        root.addView(langs);
        langState = text("", 20, Color.rgb(150, 155, 165));
        root.addView(langState);

        LinearLayout buttons = new LinearLayout(this);
        buttons.setOrientation(LinearLayout.HORIZONTAL);
        buttons.setPadding(0, 30, 0, 10);
        buttons.addView(button("Install / update", new View.OnClickListener() {
            public void onClick(View v) { installAll(); }
        }));
        buttons.addView(button("Turn all OFF", new View.OnClickListener() {
            public void onClick(View v) { setAll(false); }
        }));
        buttons.addView(button("Restart head unit", new View.OnClickListener() {
            public void onClick(View v) { confirmReboot(); }
        }));
        buttons.addView(button("Remove everything", new View.OnClickListener() {
            public void onClick(View v) { confirmRemove(); }
        }));
        root.addView(buttons);

        status = text("", 22, Color.rgb(120, 200, 140));
        status.setPadding(0, 20, 0, 0);
        root.addView(status);

        ScrollView sv = new ScrollView(this);
        sv.addView(root);
        return sv;
    }

    private TextView text(String s, int sp, int color) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextSize(sp);
        t.setTextColor(color);
        return t;
    }

    private Button button(String s, View.OnClickListener l) {
        Button btn = new Button(this);
        btn.setText(s);
        btn.setTextSize(24);
        btn.setAllCaps(false);
        btn.setOnClickListener(l);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, 110, 1f);
        lp.setMargins(0, 0, 24, 0);
        btn.setLayoutParams(lp);
        return btn;
    }

    private void setStatus(final String s) {
        Log.i(TAG, s);
        ui.post(new Runnable() { public void run() { status.setText(s); } });
    }

    private String uiLang() {
        return getSharedPreferences("lang", MODE_PRIVATE).getString("ui_lang", "en");
    }

    private String langLabel(String code) {
        for (String[] l : LANGS) if (l[0].equals(code)) return l[1];
        return code;
    }

    /** Extra-language overlays bundled in assets/ov/ (com.zeekrenglish.<code>.<short>), all codes except en. */
    private String[] langPackages() {
        try {
            java.util.ArrayList<String> l = new java.util.ArrayList<>();
            for (String f : getAssets().list("ov")) {
                if (!f.endsWith(".apk")) continue;
                String p = f.substring(0, f.length() - 4);
                for (String[] lang : LANGS) {
                    if (!lang[0].equals("en") && p.startsWith("com.zeekrenglish." + lang[0] + ".")) l.add(p);
                }
            }
            return l.toArray(new String[0]);
        } catch (Exception e) { return new String[0]; }
    }

    /** "com.zeekrenglish.uk.climate" -> "uk". */
    private static String langOf(String langPkg) {
        String rest = langPkg.substring("com.zeekrenglish.".length());
        return rest.substring(0, rest.indexOf('.'));
    }

    /** Target app of a language overlay = target of the English overlay with the same short name. */
    private static String targetOf(String langPkg) {
        String rest = langPkg.substring("com.zeekrenglish.".length());
        String ov = "com.zeekrenglish.ov." + rest.substring(rest.indexOf('.') + 1);
        for (String[] o : OVERLAYS) if (o[0].equals(ov)) return o[1];
        return null;
    }

    /** Language overlay should be ON only if its language is the chosen one. */
    private boolean langWanted(String langPkg) {
        return langOf(langPkg).equals(uiLang());
    }

    /** Sets the vehicle (HMI) language to English, same call SystemUI CarBodyStateManager uses. */
    private boolean setVehicleLanguageEnglish() {
        try {
            Object hmi = getSystemService("systemhmi");
            if (hmi == null) return false;
            String json = "{\"domain\":\"Global\",\"id\":\"locale\",\"payload\":{\"current_language\":1}}";
            Object r = hmi.getClass().getMethod("set", String.class).invoke(hmi, json);
            Log.i(TAG, "SystemHMI set language EN -> " + r);
            return Boolean.TRUE.equals(r);
        } catch (Throwable e) {
            Log.e(TAG, "SystemHMI set failed", e);
            return false;
        }
    }

    private void chooseLanguage(final String lang) {
        getSharedPreferences("lang", MODE_PRIVATE).edit().putString("ui_lang", lang).apply();
        setStatus("Switching to " + langLabel(lang) + "…");
        new Thread(new Runnable() {
            public void run() {
                boolean hmi = setVehicleLanguageEnglish();
                LangHelper.apply("en");
                Log.i(TAG, "vehicle language EN: " + hmi);
                int n = 0;
                for (String p : langPackages()) if (installed(p) >= 0 && setOverlay(p, langOf(p).equals(lang))) n++;
                setStatus(langLabel(lang) + " ON (" + n + " overlays switched). "
                        + "Reopen apps; for home screen/status bar restart the head unit.");
                ui.post(new Runnable() { public void run() { refreshLang(); } });
            }
        }).start();
    }

    private void refreshLang() {
        langState.setText("Interface text: " + langLabel(uiLang())
                + "   ·   system language stays English (keeps driver display and vehicle language consistent)");
    }

    private void refresh() {
        for (int i = 0; i < OVERLAYS.length; i++) {
            final String ov = OVERLAYS[i][0];
            boolean targetThere = installed(OVERLAYS[i][1]) >= 0;
            int ver = installed(ov);
            Boolean enabled = ver >= 0 ? overlayEnabled(ov) : null;
            final Switch sw = switches[i];
            sw.setOnCheckedChangeListener(null);
            sw.setChecked(Boolean.TRUE.equals(enabled));
            sw.setEnabled(ver >= 0 && targetThere);
            String st;
            if (!targetThere) st = "App not present on this car";
            else if (ver < 0) st = "Not installed - tap Install / update";
            else if (enabled == null) st = "Installed (state unknown)";
            else st = enabled ? "ON" : "OFF";
            states[i].setText(st);
            sw.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
                public void onCheckedChanged(CompoundButton b, final boolean on) {
                    new Thread(new Runnable() {
                        public void run() {
                            boolean ok = setOverlay(ov, on);
                            setStatus((ok ? "" : "FAILED: ") + ov + (on ? " ON" : " OFF"));
                            ui.post(new Runnable() { public void run() { refresh(); } });
                        }
                    }).start();
                }
            });
        }
    }

    // ---------------------------------------------------------------- actions

    private void installAll() {
        new Thread(new Runnable() {
            public void run() {
                int done = 0, skipped = 0, failed = 0;
                for (String[] o : OVERLAYS) {
                    if (installed(o[1]) < 0) { skipped++; continue; }
                    int bundled = bundledVersion(o[0]);
                    if (installed(o[0]) >= bundled) { skipped++; continue; }
                    setStatus("Installing " + o[2] + " ...");
                    if (installAsset("ov/" + o[0] + ".apk")) {
                        boolean on = false;
                        for (int t = 0; t < 10 && !on; t++) {   // overlay manager needs a moment
                            sleep(500);
                            on = setOverlay(o[0], true);
                        }
                        if (on) done++; else failed++;
                    } else failed++;
                }
                for (String p : langPackages()) {
                    String target = targetOf(p);
                    if (target != null && installed(target) < 0) { skipped++; continue; }   // app not on this car
                    if (installed(p) >= bundledVersion(p)) { skipped++; continue; }
                    setStatus("Installing " + langLabel(langOf(p)) + " " + p + " ...");
                    if (installAsset("ov/" + p + ".apk")) {
                        boolean ok = false;
                        for (int t2 = 0; t2 < 10 && !ok; t2++) { sleep(500); ok = setOverlay(p, langWanted(p)); }
                        if (ok) done++; else failed++;
                    } else failed++;
                }
                setStatus("Done: " + done + " installed, " + skipped + " already up to date / not applicable, "
                        + failed + " failed. Reopen the translated apps to see changes.");
                ui.post(new Runnable() { public void run() { refresh(); } });
            }
        }).start();
    }

    private void setAll(final boolean on) {
        new Thread(new Runnable() {
            public void run() {
                for (String[] o : OVERLAYS) if (installed(o[0]) >= 0) setOverlay(o[0], on);
                for (String p : langPackages()) if (installed(p) >= 0) setOverlay(p, on && langWanted(p));
                setStatus(on ? "All ON" : "All translations turned OFF - apps are back to original text");
                ui.post(new Runnable() { public void run() { refresh(); } });
            }
        }).start();
    }

    private void confirmReboot() {
        new AlertDialog.Builder(this)
                .setTitle("Restart head unit?")
                .setMessage("The screens go dark for about 1-2 minutes. Only do this while parked.")
                .setPositiveButton("Restart", (d, w) -> {
                    try {
                        ((android.os.PowerManager) getSystemService(POWER_SERVICE)).reboot(null);
                    } catch (Throwable e) {
                        setStatus("Restart failed: " + e);
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void confirmRemove() {
        new AlertDialog.Builder(this)
                .setTitle("Remove everything?")
                .setMessage("All translations will be removed and then this app will be uninstalled. "
                        + "Zeekr apps return to their original text.")
                .setPositiveButton("Remove", (d, w) -> removeAll())
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void removeAll() {
        new Thread(new Runnable() {
            public void run() {
                PackageInstaller pi = getPackageManager().getPackageInstaller();
                for (String[] o : OVERLAYS) {
                    if (installed(o[0]) < 0) continue;
                    setOverlay(o[0], false);
                    setStatus("Removing " + o[2] + " ...");
                    latch = new CountDownLatch(1);
                    pi.uninstall(o[0], resultSender());
                    await();
                }
                for (String p : langPackages()) {
                    if (installed(p) < 0) continue;
                    setOverlay(p, false);
                    latch = new CountDownLatch(1);
                    pi.uninstall(p, resultSender());
                    await();
                }
                setStatus("Translations removed. Uninstalling Zeekr English ...");
                sleep(800);
                pi.uninstall(getPackageName(), resultSender());
            }
        }).start();
    }

    // ---------------------------------------------------------------- package helpers

    private int installed(String pkg) {
        try {
            return getPackageManager().getPackageInfo(pkg, 0).versionCode;
        } catch (PackageManager.NameNotFoundException e) {
            return -1;
        }
    }

    private int bundledVersion(String ovPkg) {
        return OVERLAY_VERSION;
    }

    private String version() {
        try {
            return getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
        } catch (Exception e) {
            return "?";
        }
    }

    private boolean installAsset(String asset) {
        PackageInstaller pi = getPackageManager().getPackageInstaller();
        PackageInstaller.SessionParams p = new PackageInstaller.SessionParams(PackageInstaller.SessionParams.MODE_FULL_INSTALL);
        try {
            int id = pi.createSession(p);
            PackageInstaller.Session s = pi.openSession(id);
            try (InputStream in = getAssets().open(asset); OutputStream out = s.openWrite("base.apk", 0, -1)) {
                byte[] buf = new byte[65536];
                int n;
                while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
                s.fsync(out);
            }
            latch = new CountDownLatch(1);
            s.commit(resultSender());
            s.close();
            await();
            if (lastStatus != PackageInstaller.STATUS_SUCCESS) {
                setStatus("Install failed: " + asset + " (" + lastStatus + ") " + lastMessage);
                sleep(1500);
                return false;
            }
            return true;
        } catch (Exception e) {
            Log.e(TAG, "install " + asset, e);
            setStatus("Install error: " + e);
            sleep(1500);
            return false;
        }
    }

    private android.content.IntentSender resultSender() {
        Intent i = new Intent(ACTION_RESULT).setPackage(getPackageName());
        return PendingIntent.getBroadcast(this, (int) System.nanoTime(), i, PendingIntent.FLAG_UPDATE_CURRENT).getIntentSender();
    }

    private void await() {
        try {
            latch.await(60, TimeUnit.SECONDS);
        } catch (InterruptedException ignored) {
        }
    }

    private static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException ignored) { }
    }

    // ---------------------------------------------------------------- overlay manager (hidden API, system uid)

    private Object oms() throws Exception {
        Class<?> sm = Class.forName("android.os.ServiceManager");
        IBinder b = (IBinder) sm.getMethod("getService", String.class).invoke(null, "overlay");
        Class<?> stub = Class.forName("android.content.om.IOverlayManager$Stub");
        return stub.getMethod("asInterface", IBinder.class).invoke(null, b);
    }

    private boolean setOverlay(String pkg, boolean on) {
        try {
            Object o = oms();
            Method m = o.getClass().getMethod("setEnabled", String.class, boolean.class, int.class);
            Object r = m.invoke(o, pkg, on, USER);
            return Boolean.TRUE.equals(r) || overlayEnabledEquals(pkg, on);
        } catch (Throwable t) {
            Log.e(TAG, "setEnabled via OMS failed, trying cmd", t);
            return cmdOverlay(pkg, on);
        }
    }

    private boolean overlayEnabledEquals(String pkg, boolean on) {
        Boolean e = overlayEnabled(pkg);
        return e != null && e == on;
    }

    private Boolean overlayEnabled(String pkg) {
        try {
            Object o = oms();
            Object info = o.getClass().getMethod("getOverlayInfo", String.class, int.class).invoke(o, pkg, USER);
            if (info == null) return null;
            return (Boolean) info.getClass().getMethod("isEnabled").invoke(info);
        } catch (Throwable t) {
            Log.e(TAG, "getOverlayInfo failed", t);
            return null;
        }
    }

    private boolean cmdOverlay(String pkg, boolean on) {
        try {
            Process p = Runtime.getRuntime().exec(new String[]{"cmd", "overlay", on ? "enable" : "disable", pkg});
            return p.waitFor() == 0;
        } catch (Exception e) {
            Log.e(TAG, "cmd overlay failed", e);
            return false;
        }
    }
}
