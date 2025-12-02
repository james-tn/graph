/**
 * Mermaid syntax validator for Python subprocess calls
 * Uses mermaid-cli (mmdc) with Puppeteer for reliable validation
 * Reads Mermaid diagram code from stdin and validates syntax
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

let data = '';
process.stdin.setEncoding('utf8');

process.stdin.on('data', chunk => {
    data += chunk;
});

process.stdin.on('end', async () => {
    const diagram = data.trim();

    if (!diagram) {
        console.error('Empty diagram');
        process.exit(1);
    }

    // Create a temporary file for the diagram
    const tempDir = os.tmpdir();
    const inputFile = path.join(tempDir, `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}.mmd`);
    const outputFile = inputFile.replace('.mmd', '.svg');

    try {
        // Write diagram to temp file
        fs.writeFileSync(inputFile, diagram, 'utf8');

        // Use mmdc (mermaid-cli) to validate by attempting to render
        // Find the actual mmdc.js file
        const mmdcJs = path.join(__dirname, 'node_modules', '@mermaid-js', 'mermaid-cli', 'src', 'cli.js');
        
        // Use puppeteer config for Docker/containerized environments (--no-sandbox)
        const puppeteerConfig = path.join(__dirname, 'puppeteer-config.json');
        
        const args = [
            mmdcJs,
            '-i', inputFile,
            '-o', outputFile,
            '--quiet',
            '-p', puppeteerConfig
        ];
        
        const child = spawn('node', args, { 
            timeout: 30000  // 30 seconds for Puppeteer/Chromium startup
        });

        let stderr = '';
        let stdout = '';

        child.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        child.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        child.on('close', (code) => {
            // Clean up temp files
            try {
                if (fs.existsSync(inputFile)) fs.unlinkSync(inputFile);
                if (fs.existsSync(outputFile)) fs.unlinkSync(outputFile);
            } catch (e) {
                // Ignore cleanup errors
            }

            if (code !== 0) {
                // Extract meaningful error message
                let errorMsg = stderr || stdout || 'Unknown Mermaid syntax error';
                
                // Clean up error message
                errorMsg = errorMsg
                    .split('\n')
                    .filter(line => {
                        // Filter out noise from mmdc output
                        return !line.includes('Puppeteer old Headless') &&
                               !line.includes('chrome-headless-shell') &&
                               !line.includes('file://') &&
                               line.trim().length > 0;
                    })
                    .join('\n')
                    .trim();

                if (!errorMsg) errorMsg = 'Mermaid syntax validation failed';
                
                console.error(errorMsg);
                process.exit(1);
            } else {
                console.log('OK');
                process.exit(0);
            }
        });
    } catch (e) {
        // Clean up on error
        try {
            if (fs.existsSync(inputFile)) fs.unlinkSync(inputFile);
            if (fs.existsSync(outputFile)) fs.unlinkSync(outputFile);
        } catch (cleanupError) {
            // Ignore cleanup errors
        }
        
        console.error(e.message || String(e));
        process.exit(1);
    }
});// Handle stdin errors
process.stdin.on('error', (err) => {
    console.error('STDIN error:', err.message);
    process.exit(1);
});
