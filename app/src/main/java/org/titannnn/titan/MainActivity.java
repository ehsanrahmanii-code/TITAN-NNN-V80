package org.titannnn.titan;

import android.Manifest;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
import androidx.core.content.ContextCompat;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends AppCompatActivity {
    private WebView webView;
    private static final int REQ_PERMS = 1001;
    private static final String CHANNEL_ID = "titan_nnn_alerts";
    private static final String DASHBOARD_URL = "http://127.0.0.1:8080/";
    private final Handler handler = new Handler(Looper.getMainLooper());
    private int loadAttempts = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        createNotificationChannel();
        requestAllPermissions();

        webView = findViewById(R.id.webview);
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setBuiltInZoomControls(false);
        s.setMediaPlaybackRequiresUserGesture(false);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            s.setSafeBrowsingEnabled(false);
        }
        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                injectNotificationBridge();
            }
        });
        webView.addJavascriptInterface(new NotifyBridge(), "TitanNative");

        startPythonServer();
        scheduleLoad();
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    "Titan NNN Alerts",
                    NotificationManager.IMPORTANCE_HIGH
            );
            channel.setDescription("سیگنال و هشدارهای Titan NNN");
            channel.enableVibration(true);
            NotificationManager nm = getSystemService(NotificationManager.class);
            if (nm != null) nm.createNotificationChannel(channel);
        }
    }

    private void requestAllPermissions() {
        java.util.ArrayList<String> list = new java.util.ArrayList<>();
        if (Build.VERSION.SDK_INT >= 23) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
                    != PackageManager.PERMISSION_GRANTED) {
                list.add(Manifest.permission.WRITE_EXTERNAL_STORAGE);
                list.add(Manifest.permission.READ_EXTERNAL_STORAGE);
            }
        }
        if (Build.VERSION.SDK_INT >= 33) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED) {
                list.add(Manifest.permission.POST_NOTIFICATIONS);
            }
        }
        if (!list.isEmpty()) {
            ActivityCompat.requestPermissions(this, list.toArray(new String[0]), REQ_PERMS);
        }
    }

    private void injectNotificationBridge() {
        if (webView == null) return;
        String js =
                "(function(){\"use strict\";" +
                "if(window.__titanNativeNotify)return;window.__titanNativeNotify=1;" +
                "function show(title,body){try{if(window.TitanNative)TitanNative.notify(String(title||'Titan NNN'),String(body||''));}catch(e){}}" +
                "try{" +
                "  function N(title,opts){opts=opts||{};show(title,opts.body||'');this.title=title;this.body=opts.body||'';this.onclick=null;}" +
                "  N.permission='granted';" +
                "  N.requestPermission=function(){return Promise.resolve('granted');};" +
                "  N.prototype.close=function(){};" +
                "  window.Notification=N;" +
                "}catch(e){}" +
                "})();";
        webView.evaluateJavascript(js, null);
    }

    public class NotifyBridge {
        @JavascriptInterface
        public void notify(String title, String body) {
            handler.post(() -> postNotification(title, body));
        }
    }

    private void postNotification(String title, String body) {
        if (Build.VERSION.SDK_INT >= 33) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED) {
                return;
            }
        }
        Intent intent = new Intent(this, MainActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent pi = PendingIntent.getActivity(
                this, 0, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
        NotificationCompat.Builder b = new NotificationCompat.Builder(this, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle(title != null ? title : "Titan NNN")
                .setContentText(body != null ? body : "")
                .setStyle(new NotificationCompat.BigTextStyle().bigText(body != null ? body : ""))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setAutoCancel(true)
                .setContentIntent(pi);
        NotificationManagerCompat.from(this).notify((int) (System.currentTimeMillis() % 100000), b.build());
    }

    private void startPythonServer() {
        new Thread(() -> {
            try {
                if (!Python.isStarted()) {
                    Python.start(new AndroidPlatform(getApplicationContext()));
                }
                Python py = Python.getInstance();
                PyObject mod = py.getModule("android_main");
                mod.callAttr("start_server");
            } catch (Exception e) {
                e.printStackTrace();
                handler.post(() ->
                        Toast.makeText(MainActivity.this,
                                "Server error: " + e.getMessage(),
                                Toast.LENGTH_LONG).show());
            }
        }, "titan-python").start();
    }

    private void scheduleLoad() {
        handler.postDelayed(this::tryLoad, 3000);
    }

    private void tryLoad() {
        loadAttempts++;
        webView.loadUrl(DASHBOARD_URL);
        if (loadAttempts < 15) {
            handler.postDelayed(this::tryLoad, 2000);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
