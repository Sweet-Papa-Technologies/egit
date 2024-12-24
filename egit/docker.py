"""Docker operations for eGit."""

import time
import docker
from docker.errors import DockerException
from rich.console import Console

from egit.config import settings

console = Console()


def is_container_ready(container_id: str, timeout: int = 30) -> bool:
    """Check if Ollama container is ready to accept requests."""
    client = docker.from_env()
    container = client.containers.get(container_id)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Check container logs for ready message
            logs = container.logs(tail=10).decode('utf-8')
            if "Listening on" in logs:
                return True
        except Exception:
            pass
        time.sleep(1)
    
    return False


def pull_ollama_model() -> bool:
    """Pull the required Ollama model."""
    try:
        client = docker.from_env()
        container = client.containers.get(settings.docker_container_name)
        
        # Execute model pull command
        console.print("[yellow]Pulling Ollama model...[/yellow]")
        exec_result = container.exec_run(
            cmd=["ollama", "pull", "llama2:3b"],
            stream=True
        )
        
        # Stream the output
        for output in exec_result.output:
            console.print(output.decode().strip())
        
        return True
    except Exception as e:
        console.print(f"[red]Error pulling model: {e}[/red]")
        return False


def ensure_ollama_running() -> bool:
    """Ensure Ollama container is running with required model."""
    try:
        client = docker.from_env()
        
        # Check if container exists and is running
        try:
            container = client.containers.get(settings.docker_container_name)
            if container.status == "running":
                return True
            container.start()
            if not is_container_ready(container.id):
                console.print("[red]Container failed to start properly[/red]")
                return False
            pull_ollama_model()
            return True
        except docker.errors.NotFound:
            pass

        # Pull image if needed
        try:
            client.images.get(settings.docker_image)
        except docker.errors.ImageNotFound:
            console.print(f"[yellow]Pulling {settings.docker_image}...[/yellow]")
            client.images.pull(settings.docker_image)

        # Create and start container
        container = client.containers.run(
            settings.docker_image,
            name=settings.docker_container_name,
            detach=True,
            remove=True,
            ports={"11434/tcp": 11434},
        )
        
        if not is_container_ready(container.id):
            console.print("[red]Container failed to start properly[/red]")
            return False
            
        pull_ollama_model()
        return True

    except DockerException as e:
        console.print(f"[red]Docker error: {e}[/red]")
        return False


def stop_ollama() -> bool:
    """Stop Ollama container."""
    try:
        client = docker.from_env()
        try:
            container = client.containers.get(settings.docker_container_name)
            container.stop()
            return True
        except docker.errors.NotFound:
            return True
    except DockerException as e:
        console.print(f"[red]Docker error: {e}[/red]")
        return False
