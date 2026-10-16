FROM mcr.microsoft.com/dotnet/runtime-deps:10.0
COPY efbundle /efbundle
ENTRYPOINT ["/efbundle"]
