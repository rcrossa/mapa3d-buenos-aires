// PMTiles configuration.
// Default auto-detects from location. Override with:
//   http://localhost:8000/web/index.html?pmtiles_url=http://...
//   http://localhost:8000/web/index.html?source_layer=custom_layer_name
(function () {
  var params = new URLSearchParams(window.location.search);
  var queryUrl = params.get("pmtiles_url");
  var isFileProtocol = window.location.protocol === "file:";

  // Build default URL, handling file:// gracefully
  var defaultUrl;
  if (isFileProtocol) {
    // file:// cannot auto-detect — require explicit ?pmtiles_url=
    defaultUrl = null;
  } else {
    defaultUrl =
      window.location.protocol +
      "//" +
      window.location.host +
      "/data/tiles/buenos_aires_completo.pmtiles";
  }

  var finalUrl = queryUrl || defaultUrl;

  // Validate: only allow http/https/pmtiles schemes
  if (finalUrl && !/^(https?:\/\/|pmtiles:\/\/)/.test(finalUrl)) {
    console.error(
      "Invalid pmtiles_url scheme. Only http/https/pmtiles allowed: " +
        finalUrl
    );
    finalUrl = null;
  }

  // Hostname allowlist: warn if pmtiles_url host differs from page host
  if (finalUrl) {
    var urlHost;
    try { urlHost = new URL(finalUrl).hostname; } catch (e) { urlHost = null; }
    if (urlHost && urlHost !== window.location.hostname && urlHost !== 'localhost' && !urlHost.endsWith('.localhost')) {
      console.warn(
        "pmtiles_url host '" + urlHost + "' differs from page host. " +
          "This may be intentional for development."
      );
    }
  }

  if (!finalUrl) {
    console.warn(
      "No PMTiles URL configured. " +
        "Open via HTTP server or set ?pmtiles_url=... parameter."
    );
    var mapDiv = document.getElementById('map');
    if (mapDiv && isFileProtocol) {
      mapDiv.innerHTML =
        '<div style="color:white;background:#1e1e1e;padding:40px;text-align:center;font-family:sans-serif">' +
        '<h2>\u26a0 No se puede cargar el mapa</h2>' +
        '<p>Abre este archivo mediante el servidor HTTP:</p>' +
        '<pre style="background:#333;padding:10px">python3 web/server.py</pre>' +
        '<p>Luego visita: <code>http://localhost:8000/web/index.html</code></p></div>';
    }
  }

  window.PMTILES_CONFIG = {
    url: finalUrl,
    sourceLayer: params.get("source_layer") || null,
  };
})();
