import ipaddress
import json

def get_network_metadata(path="network/network_metadata.json"):
    with open(path) as f:
        data = json.load(f)
    return data['name'], data['cidr']

class ServerConfiguration:
    """Clase que encapsula la configuración del servidor para inyección de dependencias"""
    def __init__(self, name="hello-world", tags=None, instance_type="micro", 
                 environment="development", owner="team-infra", description=""):
        self.name = name
        self.tags = tags or {"Environment": environment, "Owner": owner, "Purpose": "demo"}
        self.instance_type = instance_type
        self.environment = environment
        self.owner = owner
        self.description = description or f"Server {name} in {environment}"

class ServerFactoryModule:
    def __init__(self, server_config, metadata_path="network/network_metadata.json"):
        # Inyección de dependencias: recibe configuración del servidor
        self._config = server_config
        self._name = server_config.name
        
        # Obtiene información de la red (dependencia externa)
        network_name, cidr = get_network_metadata(metadata_path)
        self._network = network_name
        self._network_ip = self._allocate_fifth_ip_address_in_range(cidr)
        self.resources = self._build()

    def _allocate_fifth_ip_address_in_range(self, ip_range):
        network = ipaddress.IPv4Network(ip_range)
        return str(list(network.hosts())[4])

    def _build(self):
        # Construye la configuración de Terraform con todos los parámetros inyectados
        return {
            "resource": {
                "null_resource": {
                    "server": {
                        "triggers": {
                            "name": self._config.name,
                            "subnetwork": self._network,
                            "network_ip": self._network_ip,
                            "instance_type": self._config.instance_type,
                            "environment": self._config.environment,
                            "owner": self._config.owner,
                            "description": self._config.description,
                            "tags": json.dumps(self._config.tags, sort_keys=True)
                        },
                        "provisioner": [{
                            "local-exec": {
                                "command": (
                                    f"echo 'Server {self._config.name}' && "
                                    f"echo '  Descripción: {self._config.description}' && "
                                    f"echo '  Tipo: {self._config.instance_type}' && "
                                    f"echo '  Entorno: {self._config.environment}' && "
                                    f"echo '  Propietario: {self._config.owner}' && "
                                    f"echo '  Red: {self._network}' && "
                                    f"echo '  IP asignada: {self._network_ip}' && "
                                    f"echo '  Etiquetas: {json.dumps(self._config.tags)}'"
                                )
                            }
                        }]
                    }
                }
            }
        }

if __name__ == "__main__":
    # Inversión de control: la configuración se inyecta desde afuera
    server_config = ServerConfiguration(
        name="web-server-prod",
        tags={
            "Environment": "production",
            "Team": "backend",
            "Application": "web-service",
            "Backup": "daily",
            "Monitoring": "enabled"
        },
        instance_type="small",
        environment="production", 
        owner="backend-team",
        description="Servidor web principal para aplicación de producción"
    )
    
    # El factory recibe la configuración como dependencia
    server = ServerFactoryModule(server_config)
    with open('server.tf.json', 'w') as f:
        json.dump(server.resources, f, sort_keys=True, indent=4)
