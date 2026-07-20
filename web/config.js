// PMTiles configuration.
// Override at runtime with: http://localhost:8000/web/index.html?pmtiles_url=...
(function () {
  const params = new URLSearchParams(window.location.search);
  const queryUrl = params.get("pmtiles_url");
  const defaultUrl =
    window.location.protocol +
    "//" +
    window.location.host +
    "/data/tiles/buenos_aires_completo.pmtiles";

  window.PMTILES_CONFIG = {
    url: queryUrl || defaultUrl,
  };
})();
