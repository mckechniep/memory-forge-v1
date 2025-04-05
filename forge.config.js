// forge.config.js
// This file configures how Electron Forge packages and distributes the application
// It defines what files to include, security settings, and build targets

// Import the FusesPlugin which allows setting security restrictions on the Electron app
const { FusesPlugin } = require('@electron-forge/plugin-fuses');
// Import security configuration options for the Electron app
const { FuseV1Options, FuseVersion } = require('@electron/fuses');
// Import path module for handling file paths
const path = require('path');

module.exports = {
  // Configuration for how the application should be packaged
  packagerConfig: {
    // Enable ASAR archive format which improves performance and security
    asar: true,
    // List of directories to exclude from the final package
    ignore: [
      'backend/venv', // ignore Python virtual environment to reduce size
      'dist',         // ignore built frontend artifacts
      'out',          // ignore packaging output directory
    ],
    // Additional resources to include that should be accessible to the app
    extraResource: [
      path.resolve(__dirname, 'backend'), // include backend code as a resource
    ],
  },
  
  // Configuration for rebuilding native modules (using default settings)
  rebuildConfig: {},
  
  // Define different package formats for distribution
  // Each "maker" creates a different type of installer or package
  makers: [
    {
      // Create a simple ZIP archive package
      name: '@electron-forge/maker-zip',
      config: {
        // Additional files to include in the ZIP that aren't part of the app itself
        extraFiles: [
          {
            // Copy setup.bat from the project root to the package
            from: path.resolve(__dirname, 'setup.bat'),
            to: 'setup.bat',
          },
        ],
      },
    },
    {
      // Create Debian (.deb) packages for Linux distributions
      name: '@electron-forge/maker-deb',
      config: {},
    },
    {
      // Create RPM packages for Linux distributions like Fedora
      name: '@electron-forge/maker-rpm',
      config: {},
    },
  ],
  
  // Plugins extend Electron Forge's functionality during the build process
  plugins: [
    {
      // Automatically extract native modules for better performance
      name: '@electron-forge/plugin-auto-unpack-natives',
      config: {},
    },
    // Configure security settings using Fuses
    // Fuses are security restrictions that can't be changed after packaging
    new FusesPlugin({
      version: FuseVersion.V1,
      // Prevent the app from being used as a Node.js runtime
      [FuseV1Options.RunAsNode]: false,
      // Enable encryption for cookies stored by the app
      [FuseV1Options.EnableCookieEncryption]: true,
      // Disable the ability to use NODE_OPTIONS environment variable
      [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
      // Disable Node.js CLI debugging features for security
      [FuseV1Options.EnableNodeCliInspectArguments]: false,
      // Enable validation of the ASAR archive integrity
      [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
      // Only allow loading the app from the ASAR archive (security feature)
      [FuseV1Options.OnlyLoadAppFromAsar]: true,
    }),
  ],
  
  // Hooks allow running custom code at specific points during the build process
  hooks: {
    // This hook runs after files are copied to the build directory but before packaging
    // Inputs: config object, build path, Electron version, platform, and architecture
    // Output: Copies setup.bat to the build directory if it exists
    packageAfterCopy: async (config, buildPath, electronVersion, platform, arch) => {
      const fs = require('fs');
      // Get the path to setup.bat in the project root
      const setupBatPath = path.resolve(__dirname, 'setup.bat');
      // Define where to copy it in the build directory
      const destPath = path.join(buildPath, 'setup.bat');
      
      // Check if setup.bat exists and copy it to the build directory
      if (fs.existsSync(setupBatPath)) {
        fs.copyFileSync(setupBatPath, destPath);
        console.log(`Copied setup.bat to ${destPath}`);
      } else {
        console.error(`setup.bat not found at ${setupBatPath}`);
      }
    }
  }
};
