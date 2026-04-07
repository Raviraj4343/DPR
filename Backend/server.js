const express = require("express");
const cors = require("cors");
const helmet = require("helmet");
const morgan = require("morgan");

const { env } = require("./config/env");
const apiRoutes = require("./routes");
const notFound = require("./middleware/notFound");
const errorHandler = require("./middleware/errorHandler");

const app = express();

const allowedOrigins = new Set(env.CORS_ORIGINS || []);

const corsOptions = {
	origin(origin, callback) {
		// Requests without Origin (curl/postman/server-to-server) do not require CORS.
		if (!origin) {
			return callback(null, false);
		}

		if (env.CORS_ALLOW_ALL || allowedOrigins.has(origin)) {
			// Return the exact request origin so the response contains a single valid value.
			return callback(null, origin);
		}

		return callback(new Error("Not allowed by CORS"));
	},
	credentials: false,
	optionsSuccessStatus: 204,
};

app.use(helmet());
app.use(cors(corsOptions));
app.options("*", cors(corsOptions));
app.use(express.json({ limit: "1mb" }));
app.use(morgan("dev"));

app.use("/api/v1", apiRoutes);

app.use(notFound);
app.use(errorHandler);

app.listen(env.PORT, () => {
	console.log(`Backend running on http://localhost:${env.PORT}`);
	console.log(`ML service target: ${env.ML_SERVICE_URL}`);
	console.log(`CORS allow all: ${env.CORS_ALLOW_ALL}`);
	console.log(`CORS allowlist: ${env.CORS_ORIGINS.join(", ") || "(none)"}`);
});

