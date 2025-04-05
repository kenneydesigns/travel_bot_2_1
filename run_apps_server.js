const express = require('express');
const { exec } = require('child_process');

const app = express();
const port = 3000;

// Serve static files from the "public" folder
app.use(express.static('public'));

// Endpoint to run TravelBot (context mode)
app.get('/run/travelbot', (req, res) => {
  exec('python3 src/travelbot.py --mode context', (error, stdout, stderr) => {
    if (error) {
      return res.status(500).send(`Error: ${stderr}`);
    }
    res.send(`Output:\n${stdout}`);
  });
});

// Endpoint to run ChunkBot
app.get('/run/chunkbot', (req, res) => {
  exec('python3 src/chunkbot.py', (error, stdout, stderr) => {
    if (error) {
      return res.status(500).send(`Error: ${stderr}`);
    }
    res.send(`Output:\n${stdout}`);
  });
});

// Endpoint to run SimpleBot
app.get('/run/simplebot', (req, res) => {
  exec('python3 src/simplebot.py', (error, stdout, stderr) => {
    if (error) {
      return res.status(500).send(`Error: ${stderr}`);
    }
    res.send(`Output:\n${stdout}`);
  });
});

// Endpoint to run Batch Test
app.get('/run/batch_test', (req, res) => {
  exec('python3 src/batch_test.py', (error, stdout, stderr) => {
    if (error) {
      return res.status(500).send(`Error: ${stderr}`);
    }
    res.send(`Output:\n${stdout}`);
  });
});

// Endpoint to run Batch Test Hybrid
app.get('/run/batch_test_hybrid', (req, res) => {
  exec('python3 src/batch_test_hybrid.py', (error, stdout, stderr) => {
    if (error) {
      return res.status(500).send(`Error: ${stderr}`);
    }
    res.send(`Output:\n${stdout}`);
  });
});

app.listen(port, () => {
  console.log(`Run Apps server listening at http://localhost:${port}`);
});