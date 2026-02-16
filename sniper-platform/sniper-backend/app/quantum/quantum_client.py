from __future__ import annotations


class IBMQuantumClient:
    def __init__(self) -> None:
        self.connected = False
        self.api_token = None

    def connect(self, api_token: str) -> None:
        self.api_token = api_token
        self.connected = bool(api_token)

    def get_available_backends(self) -> list[str]:
        return ['ibm_brisbane', 'ibm_kyoto', 'ibm_sherbrooke']

    def submit_job(self, circuit: dict, backend: str, shots: int) -> dict:
        _ = circuit
        _ = shots
        if not self.connected:
            raise RuntimeError('IBM Quantum client is not connected')
        return {'job_id': f'{backend}-job-001', 'backend': backend}

    def get_job_result(self, job_id: str) -> dict:
        return {'job_id': job_id, 'result': {'counts': {'0000': 400, '1111': 600}}}

    def estimate_cost(self, circuit: dict, shots: int) -> float:
        _ = circuit
        return float(shots) * 0.0001
