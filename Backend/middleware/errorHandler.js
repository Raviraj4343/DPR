function errorHandler(err, req, res, next) {
  const statusCode =
    err.response?.status || err.statusCode || (err.name === "SyntaxError" ? 400 : 500);

  const upstreamError = err.details || err.response?.data;

  return res.status(statusCode).json({
    success: false,
    message: err.message || "Internal server error",
    details: upstreamError || undefined,
  });
}

module.exports = errorHandler;
