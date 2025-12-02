/**
 * Persistent Mermaid validation service
 * Keeps a single Puppeteer browser instance running to avoid repeated startup overhead
 */

const puppeteer = require('puppeteer');
const readline = require('readline');

let browser = null;
let page = null;

async function initBrowser() {
    if (browser) return;
    
    const config = require('./puppeteer-config.json');
    browser = await puppeteer.launch({
        headless: config.headless || 'new',
        args: config.args || []
    });
    page = await browser.newPage();
    
    // Load Mermaid library
    await page.addScriptTag({
        url: 'https://cdn.jsdelivr.net/npm/mermaid@11.4.0/dist/mermaid.min.js'
    });
    
    // Initialize Mermaid
    await page.evaluate(() => {
        mermaid.initialize({ 
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'strict'
        });
    });
}

async function validateDiagram(diagram) {
    try {
        await initBrowser();
        
        const result = await page.evaluate(async (diagramCode) => {
            try {
                // Use mermaid.parse() for validation
                await mermaid.parse(diagramCode);
                return { valid: true };
            } catch (error) {
                return { 
                    valid: false, 
                    error: error.message || 'Unknown syntax error'
                };
            }
        }, diagram);
        
        return result;
    } catch (error) {
        return { 
            valid: false, 
            error: error.message 
        };
    }
}

async function shutdown() {
    if (browser) {
        await browser.close();
        browser = null;
        page = null;
    }
}

// Handle line-by-line input for validation requests
async function main() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        terminal: false
    });

    let buffer = '';
    
    rl.on('line', (line) => {
        if (line === '<<<END>>>') {
            // Process accumulated diagram
            validateDiagram(buffer).then(result => {
                if (result.valid) {
                    console.log('OK');
                } else {
                    console.error(result.error);
                }
                buffer = '';
            });
        } else {
            buffer += line + '\n';
        }
    });

    rl.on('close', async () => {
        await shutdown();
        process.exit(0);
    });

    // Handle termination signals
    process.on('SIGTERM', async () => {
        await shutdown();
        process.exit(0);
    });

    process.on('SIGINT', async () => {
        await shutdown();
        process.exit(0);
    });
}

main().catch(async (error) => {
    console.error('Service error:', error);
    await shutdown();
    process.exit(1);
});
