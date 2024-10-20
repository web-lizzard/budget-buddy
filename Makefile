test:
	docker compose exec server sh -c "dotnet test --logger 'console;verbosity=normal'"
