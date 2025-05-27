library(tidyr)
library(ggplot2)

data <- read.csv("bali3_benchmark.csv")

long_data <- data %>%
  pivot_longer(cols = c(MUSCLE_time, Pre_time, Post_time),
               names_to = "algorithm",
               values_to = "time")

long_data$algorithm <- factor(long_data$algorithm, levels = c("MUSCLE_time", "Pre_time", "Post_time"))

plot2 <- ggplot(long_data, aes(x = algorithm, y = time, fill = algorithm)) +
  geom_boxplot() +
  scale_y_log10() +
  theme_minimal() +
  labs(title = "B", x = "Algorithm", y = "Time (log scale, seconds)") +
  scale_x_discrete(labels = c("MUSCLE_time" = "MUSCLE", 
                              "Pre_time" = "Pre-Processing", 
                              "Post_time" = "Post-Processing")) +
  expand_limits(y = c(1, NA)) +
  theme(legend.position = "none")

plot3 <- ggplot(data, aes(x = MUSCLE_time, y = Merge_time)) +
  geom_point(color = "blue", size = 2) +
  geom_abline(slope = 1, intercept = 0, color = "red", linetype = "dashed") +
  scale_x_continuous(limits = c(min(data$MUSCLE_time), max(data$MUSCLE_time))) +
  scale_y_continuous(limits = c(min(data$Merge_time), max(data$Merge_time))) +
  theme_minimal() +
  labs(title = "A",
       x = "MUSCLE Runtime (seconds)", y = "Total MergeAlign Runtime (seconds)")



plot1 <- ggplot(data, aes(x = Pre_time, y = Merge_time)) +
  geom_point(color = "blue", size = 2) +
  geom_abline(slope = 1, intercept = 0, color = "red", linetype = "dashed") +
  scale_x_continuous(limits = c(min(data$Pre_time), max(data$Pre_time))) +
  scale_y_continuous(limits = c(min(data$Merge_time), max(data$Merge_time))) +
  theme_minimal() +
  labs(title = "A",
       x = "MergeAlign Pre-processing Time (seconds)", y = "Total MergeAlign Runtime (seconds)")

long_data2 <- data %>%
  pivot_longer(cols = c(Pre_time, Post_time, Merge_time),
               names_to = "algorithm",
               values_to = "time") %>%
  mutate(algorithm = factor(algorithm, 
                            levels = c("Pre_time", "Post_time", "Merge_time"),
                            labels = c("Pre-processing", "Post-processing", "Total")))

plot4 <- ggplot(long_data2, aes(x = algorithm, y = time, fill = algorithm)) +
  geom_boxplot(outlier.shape = NA) +
  theme_minimal() +
  labs(title = "B", 
       x = "Processing Step", y = "Time (seconds)") +
  scale_fill_brewer(palette = "Set3") +
  theme(
    plot.title = element_text(hjust = 0),
    axis.text.x = element_text(angle = 45, hjust = 1),
    legend.position = "none"
  ) +
  coord_cartesian(ylim = c(0, 800))

plot1 + plot4 #pre/post processing
plot3 + plot2 #muscle vs merge

# Wilcoxon test
data$diff <- data$Merge_time - data$MUSCLE_time

ggplot(data, aes(x = diff)) + 
  geom_histogram(bins = 10, fill = "skyblue", color = "black")

shapiro.test(data$diff)

wilcox_test_result <- wilcox.test(data$MergeAlign_F, data$MUSCLE_F, paired = TRUE)

print(wilcox_test_result)
