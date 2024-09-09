const express = require('express');
const app = express();
const { exec } = require('child_process');
const path = require('path');
const { Pool } = require('pg');
const cors = require('cors');
const { CallTracker } = require('assert');
const axios = require('axios'); // Import axios for making HTTP requests
const port = 3000;
let site = "";
let past_site = "";
const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'scraping',
    password: 'Datakmkc@42069',
    port: 5432,
  });
  app.use(cors());
app.get('/run-script', (req, res) => {
    console.log("hi")
    exec(`python ./script/combined-v1.py ${site}`, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing script: ${error}`);
        return res.status(500).send('Error executing script');
      }
      if (stderr) {
        console.error(`Script error: ${stderr}`);
        return res.status(500).send('Script error');
      }
      console.log(`Script output: ${stdout}`);
      res.send(stdout);
    });
  });

         
  async function getFlavorId(flavorName) {
    try {
      const result = await pool.query(
        `SELECT flavor_id
         FROM Flavor
         WHERE flavor_name = $1`,
        [flavorName]
      );
  
      // Check if a row was returned
      if (result.rows.length > 0) {
        return result.rows[0].flavor_id;
      } else {
        console.log(`Flavor "${flavorName}" not found.`);
        return null;
      }
    } 
    catch{
      return false;
    }

  }

  async function isDatabaseEmpty() {
    try {
      const queryText = 'SELECT 1 FROM Beverage LIMIT 1';
      const result = await pool.query(queryText);
  
      return result.rows.length === 0;
    } catch (error) {
      console.error('Error checking if database is empty:', error);
      return true;
    }
  }
  
  
  app.get('/beverages', async (req, res) => {
    const { brand, flavor, website } = req.query;
    site = website;
    present_site = website;
    console.log(site);
    if (!brand) {
      return res.status(400).send('Brand query parameter is required.');
    }
  
    try {
      const databaseIsEmpty = await isDatabaseEmpty(brand, flavor);
  
      if (present_site != past_site) {
        console.log('Database is empty, running script...');
        const scriptResponse = await axios.get('http://localhost:3000/run-script');
  
        // console.log('Script completed:', scriptResponse.data);
  
        // Optionally, wait for a few seconds to ensure the script has completed and data is available
        await new Promise(resolve => setTimeout(resolve, 5000)); // wait for 5 seconds
      }
      
      past_site = site;
      let queryText = `
        SELECT 
            b.beverage_id,
            p.name AS product_name,
            br.brand_name,
            f.flavor_name,
            b.price,
            b.discount,
            b.mrp,
            b.volume,
            b.quantity,
            l.name AS location_name,
            w.name AS website_name
        FROM 
            Beverage b
        JOIN 
            Product p ON b.product_id = p.product_id
        JOIN 
            Brand br ON p.brand_id = br.brand_id
        JOIN 
            Flavor f ON p.flavor_id = f.flavor_id
        LEFT JOIN 
            BeverageLocation bl ON b.beverage_id = bl.beverage_id
        LEFT JOIN 
            Location l ON bl.location_id = l.location_id
        LEFT JOIN 
            Website w ON bl.site_id = w.site_id
        WHERE 
            br.brand_name = $1`;
  
      const queryParams = [brand];
  
      if (flavor) {
        queryText += ` AND f.flavor_name = $2`;
        queryParams.push(flavor);
      }
  
      const result = await pool.query(queryText, queryParams);
  
      res.json(result.rows);
    } catch (err) {
      console.error('Error executing query', err);
      res.status(500).send('Internal Server Error');
    }
  });
  
  app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
  });