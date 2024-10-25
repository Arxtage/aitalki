// import { Construct } from "constructs";
// import { App, TerraformStack } from "cdktf";

// class MyStack extends TerraformStack {
//   constructor(scope: Construct, id: string) {
//     super(scope, id);

//     // define resources here
//   }
// }

// const app = new App();
// new MyStack(app, "infra");
// app.synth();

import { Construct } from 'constructs';
import { App, TerraformStack } from 'cdktf';
import { HcloudProvider } from "./.gen/providers/hcloud/provider";
import { DockerProvider, DockerCompose } from '@cdktf/provider-docker';


class MyHetznerStack extends TerraformStack {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    // Configure Hetzner Provider
    new HetznerProvider(this, 'Hetzner', {
      token: process.env.HETZNER_TOKEN,
    });

    // Create a Hetzner Server
    const server = new Server(this, 'server', {
      name: 'docker-server',
      image: 'ubuntu-20.04',
      serverType: 'cx11', // Choose a server type
      location: 'nbg1', // Location e.g., 'nbg1', 'fsn1'
    });

    // Configure Docker Provider on the Server
    new DockerProvider(this, 'docker', {
      host: `tcp://${server.publicIp}:2375`,
    });

    // Add Docker Compose Configuration
    new DockerCompose(this, 'docker-compose', {
      path: './docker-compose.yml',
    });
  }
}
