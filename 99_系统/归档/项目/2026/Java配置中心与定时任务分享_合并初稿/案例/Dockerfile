# 构建、测试和运行均在容器中完成，宿主机不需要安装 Java 或 Maven。
FROM maven:3.9.9-eclipse-temurin-17 AS build
WORKDIR /workspace
COPY pom.xml .
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B -ntp verify

FROM eclipse-temurin:17-jre-jammy
WORKDIR /app
COPY --from=build /workspace/target/demo.jar /app/demo.jar
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/demo.jar"]
