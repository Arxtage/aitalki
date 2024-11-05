# frontend/Dockerfile
FROM node:16

# Set the working directory for the frontend
WORKDIR /frontend

# Copy the package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Create a directory for vad files
RUN mkdir -p public

# Copy the necessary files from node_modules to the public directory
RUN cp node_modules/@ricky0123/vad-web/dist/silero_vad.onnx public/ && \
    cp node_modules/@ricky0123/vad-web/dist/vad.worklet.bundle.min.js public/ && \
    cp node_modules/onnxruntime-web/dist/* public/

# Install `serve` globally to serve the production build
RUN npm install -g serve

# Copy the rest of the frontend code
COPY . .

# Build the React app for production
RUN npm run build

# Expose the port that the app runs on
EXPOSE 3000

# Start the production build using `serve`
CMD ["serve", "-s", "build", "-l", "3000"]
