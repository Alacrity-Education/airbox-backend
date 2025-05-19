const { Point } = require("@influxdata/influxdb-client");
const { influxDB, INFLUX_ORG, INFLUX_BUCKET } = require("../config/influxdb");

const queryApi = influxDB.getQueryApi(INFLUX_ORG);

exports.insertData = async (req, res) => {
  try {
    const { measurement, fields, tags } = req.body;

    if (!measurement || !fields) {
      return res.status(400).json({ error: "Measurement and fields are required" });
    }

    const writeApi = influxDB.getWriteApi(INFLUX_ORG, INFLUX_BUCKET);
    const point = new Point(measurement);

    for (const key in fields) {
      point.floatField(key, fields[key]);
    }

    if (tags) {
      for (const key in tags) {
        point.tag(key, tags[key]);
      }
    }

    writeApi.writePoint(point);
    await writeApi.flush();
    await writeApi.close();

    res.status(201).json({ message: "Data inserted successfully" });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.getData = async (req, res) => {
  try {
    const { measurement, start = "-1h", stop = "now()" } = req.query;

    if (!measurement) {
      return res.status(400).json({ error: "Measurement is required" });
    }

    const query = `
      from(bucket: "${INFLUX_BUCKET}")
        |> range(start: ${start}, stop: ${stop})
        |> filter(fn: (r) => r._measurement == "${measurement}")
    `;

    const results = [];
    await queryApi.queryRows(query, {
      next(row, tableMeta) {
        results.push(tableMeta.toObject(row));
      },
      error(error) {
        console.error("Query error:", error);
        res.status(500).json({ error: error.message });
      },
      complete() {
        res.status(200).json(results);
      },
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.deleteData = async (req, res) => {
  try {
    const { measurement, tags } = req.body;

    if (!measurement) {
      return res.status(400).json({ error: "Measurement is required" });
    }

    const writeApi = influxDB.getWriteApi(INFLUX_ORG, INFLUX_BUCKET);
    const point = new Point(measurement);

    if (tags) {
      for (const key in tags) {
        point.tag(key, tags[key]);
      }
    }

    point.floatField("deleted", 1);
    writeApi.writePoint(point);
    await writeApi.flush();
    await writeApi.close();

    res.status(200).json({ message: "Data marked as deleted" });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
