# =============================================================================
# CULTURE AND MACROECONOMIC PERFORMANCE
# Cannata & Biondo (2026)
# PCA-Based Work Ethic Index -- Italian Regions and European Countries
# =============================================================================

# --- Environment setup -------------------------------------------------------
rm(list = ls())
if (!is.null(dev.list())) dev.off()
cat("\014")

# --- Packages ----------------------------------------------------------------
libs <- c(
  "tidyverse", "janitor", "psych", "factoextra", "sf",
  "rnaturalearth", "rnaturalearthdata", "ggplot2",
  "dplyr", "geodata", "scales", "readxl", "here"
)
missing_libs <- setdiff(libs, rownames(installed.packages()))
if (length(missing_libs) > 0) install.packages(missing_libs, dependencies = TRUE)
suppressMessages(lapply(libs, library, character.only = TRUE))


# =============================================================================
# PART I: ITALIAN REGIONS
# =============================================================================

# --- Data --------------------------------------------------------------------
data0_it <- read_excel(here("Figures", "DatasetIT.xlsx")) %>% clean_names()

# --- Variable transformation -------------------------------------------------
# Negative indicators inverted so that higher values reflect stronger work ethic.
data1_it <- data0_it %>%
  transmute(
    region,
    emp_rate   = emp_rate,
    edu_sec    = edu_upper_sec,
    tert_grad  = tert_grad,
    lifelong   = lifelong_learn,
    job_sat    = job_sat,
    neet_inv   = 100 - neet_share,
    irreg_inv  = 100 - informal_rate,
    absent_inv = 100 - absent_rate
  )

# --- Standardization ---------------------------------------------------------
regions <- data1_it$region
Z_it    <- data1_it %>% select(-region) %>% scale()

# --- Adequacy tests ----------------------------------------------------------
R_it          <- cor(Z_it, use = "pairwise.complete.obs")
bartlett_it   <- cortest.bartlett(R_it, n = nrow(Z_it))
kmo_it        <- KMO(R_it)

print(bartlett_it)
print(kmo_it)

# --- PCA (scree plot) --------------------------------------------------------
pca_it <- prcomp(Z_it, scale. = FALSE)

fviz_eig(
  pca_it,
  addlabels = TRUE,
  barfill   = "#2C5F8A",
  barcolor  = "black",
  linecolor = "#C0392B",
  ylim      = c(0, 80)
) +
  ggtitle("") +
  labs(x = "Principal Component", y = "Percentage of Explained Variance") +
  theme_classic() +
  theme(
    axis.text    = element_text(size = 11),
    axis.title   = element_text(size = 12),
    plot.caption = element_blank()
  )

ggsave(here("Figures", "scree_plot_italy.pdf"), width = 7, height = 4.5, dpi = 300)
summary(pca_it)

# --- Work Ethic Index (PC1) --------------------------------------------------
# PC1 sign is negated so that higher scores reflect stronger work ethic.
# WEI is then min-max normalized to [0, 1].
wei_it <- data.frame(
  region    = regions,
  pc1_score = -pca_it$x[, 1]
) %>%
  mutate(
    WEI = (pc1_score - min(pc1_score)) /
          (max(pc1_score) - min(pc1_score))
  ) %>%
  arrange(desc(WEI))

print(wei_it)

# --- Choropleth map ----------------------------------------------------------
italy <- geodata::gadm(country = "Italy", level = 1, path = tempdir()) %>%
  st_as_sf() %>%
  rename(region_it = NAME_1)

# Name correspondence between GADM shapefile and dataset
correspondence <- data.frame(
  map_name  = c("Piemonte", "Valle d'Aosta", "Lombardia",
                "Trentino-Alto Adige", "Veneto", "Friuli-Venezia Giulia",
                "Liguria", "Emilia-Romagna", "Toscana", "Umbria", "Marche",
                "Lazio", "Abruzzo", "Molise", "Campania", "Apulia",
                "Basilicata", "Calabria", "Sicily", "Sardegna"),
  data_name = c("Piemonte", "Valle d'Aosta", "Lombardia",
                "Trentino Alto Adige/Sudtirol", "Veneto",
                "Friuli-Venezia Giulia", "Liguria", "Emilia-Romagna",
                "Toscana", "Umbria", "Marche", "Lazio", "Abruzzo", "Molise",
                "Campania", "Puglia", "Basilicata", "Calabria",
                "Sicilia", "Sardegna")
)

italy <- italy %>%
  left_join(correspondence, by = c("region_it" = "map_name")) %>%
  left_join(wei_it, by = c("data_name" = "region"))

stopifnot(sum(is.na(italy$WEI)) == 0)

ggplot(italy) +
  geom_sf(aes(fill = WEI), color = "white", size = 0.3) +
  scale_fill_gradient(
    low    = "#DEEBF7",
    high   = "#08306B",
    name   = "Work Ethic Index",
    labels = number_format(accuracy = 0.01)
  ) +
  theme_minimal() +
  labs(caption = "Source: own computation based on regional data (ISTAT)") +
  theme(
    axis.text       = element_blank(),
    axis.ticks      = element_blank(),
    panel.grid      = element_blank(),
    legend.position = "right"
  )

ggsave(here("Figures", "wei_map_italy.pdf"), width = 6, height = 7, dpi = 300)

# --- Factor analysis: parallel test ------------------------------------------
fa.parallel(Z_it, fa = "fa", n.iter = 100, show.legend = TRUE, main = "")

# --- Factor analysis: one-factor ML model ------------------------------------
fa1_it <- psych::fa(Z_it, nfactors = 1, fm = "ml", rotate = "none",
                    scores = "tenBerge")
print(fa1_it, digits = 3, cut = 0.30)

# --- PCA vs FA rank comparison -----------------------------------------------
fa_scores_it <- as.data.frame(fa1_it$scores)
fa_scores_it$region      <- regions
colnames(fa_scores_it)[1] <- "FA_score"

comparison_it <- left_join(wei_it, fa_scores_it, by = "region") %>%
  mutate(
    rank_PCA = rank(-WEI),
    rank_FA  = rank(-FA_score)
  )

cor_test_it <- cor.test(comparison_it$WEI, comparison_it$FA_score)
print(cor_test_it)

ggplot(comparison_it, aes(x = rank_PCA, y = rank_FA, label = region)) +
  geom_point(color = "steelblue", size = 3) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "grey40") +
  geom_text(nudge_y = 0.5, size = 3) +
  theme_minimal() +
  labs(
    x = "Rank by PCA (Work Ethic Index)",
    y = "Rank by Factor Analysis"
  ) +
  theme(
    axis.text  = element_text(size = 10),
    axis.title = element_text(size = 10)
  )

ggsave(here("Figures", "pca_fa_italy.pdf"), width = 7, height = 6, dpi = 300)


# =============================================================================
# PART II: EUROPEAN COUNTRIES
# =============================================================================

# --- Data --------------------------------------------------------------------
data0_eu <- read_excel(here("Figures", "DataEU.xlsx")) %>% clean_names()

# --- Variable transformation -------------------------------------------------
# Negative indicators inverted so that higher values reflect stronger work ethic.
# Note: absent_inv is excluded from the European PCA (item-level KMO < 0.50).
data1_eu <- data0_eu %>%
  transmute(
    country    = countries,
    emp_rate   = emp_rate,
    edu_sec    = edu_upper_sec,
    tert_grad  = tert_grad,
    lifelong   = lifelong_learn,
    job_sat    = job_sat,
    neet_inv   = 100 - neet_share,
    shadow_inv = 100 - shadow_rate
  )

# --- Standardization ---------------------------------------------------------
countries <- data1_eu$country
Z_eu      <- data1_eu %>% select(-country) %>% scale()

# --- Adequacy tests (full variable set) --------------------------------------
R_eu        <- cor(Z_eu, use = "pairwise.complete.obs")
bartlett_eu <- cortest.bartlett(R_eu, n = nrow(Z_eu))
kmo_eu      <- KMO(R_eu)

cat("Bartlett's test: chi2 =", round(bartlett_eu$chisq, 3),
    ", df =", bartlett_eu$df,
    ", p-value =", format(bartlett_eu$p.value, scientific = TRUE), "\n")
cat("Overall KMO:", round(kmo_eu$MSA, 3), "\n")
print(round(kmo_eu$MSAi, 3))

# --- Drop low-KMO variables and re-run adequacy tests ------------------------
# absent_inv and job_sat removed: item-level MSA falls below 0.50.
Z_eu <- data1_eu %>% select(-country, -absent_inv, -job_sat) %>% scale()

R_eu        <- cor(Z_eu, use = "pairwise.complete.obs")
bartlett_eu <- cortest.bartlett(R_eu, n = nrow(Z_eu))
kmo_eu      <- KMO(R_eu)

cat("Bartlett's test (reduced): chi2 =", round(bartlett_eu$chisq, 3),
    ", df =", bartlett_eu$df,
    ", p-value =", format(bartlett_eu$p.value, scientific = TRUE), "\n")
cat("Overall KMO (reduced):", round(kmo_eu$MSA, 3), "\n")
print(round(kmo_eu$MSAi, 3))

# --- PCA (scree plot) --------------------------------------------------------
pca_eu <- prcomp(Z_eu, scale. = FALSE)

fviz_eig(
  pca_eu,
  addlabels = TRUE,
  barfill   = "#2C5F8A",
  barcolor  = "black",
  linecolor = "#C0392B",
  ylim      = c(0, 80)
) +
  ggtitle("") +
  labs(x = "Principal Component", y = "Percentage of Explained Variance") +
  theme_classic() +
  theme(
    axis.text    = element_text(size = 11),
    axis.title   = element_text(size = 12),
    plot.caption = element_blank()
  )

ggsave(here("Figures", "scree_plot_eu.pdf"), width = 7, height = 4.5, dpi = 300)
summary(pca_eu)

# --- Work Ethic Index (PC1) --------------------------------------------------
# PC1 sign is negated so that higher scores reflect stronger work ethic.
# WEI is then min-max normalized to [0, 1].
wei_eu <- data.frame(
  country   = countries,
  pc1_score = -pca_eu$x[, 1]
) %>%
  mutate(
    WEI = (pc1_score - min(pc1_score)) /
          (max(pc1_score) - min(pc1_score))
  ) %>%
  arrange(desc(WEI))

print(wei_eu)

# --- Choropleth map ----------------------------------------------------------
world     <- ne_countries(scale = "medium", returnclass = "sf")
world$WEI <- NA_real_
world$WEI[match(wei_eu$country, world$admin)] <- wei_eu$WEI

ggplot(world) +
  geom_sf(aes(fill = WEI), color = "white", size = 0.2) +
  scale_fill_gradient(
    low      = "#FFCCCC",
    high     = "#990000",
    name     = "Work Ethic Index",
    labels   = number_format(accuracy = 0.01),
    na.value = "grey90"
  ) +
  coord_sf(xlim = c(-15, 45), ylim = c(34, 72), expand = FALSE) +
  theme_minimal() +
  labs(title = "", subtitle = "", caption = "") +
  theme(
    axis.text       = element_blank(),
    axis.ticks      = element_blank(),
    panel.grid      = element_blank(),
    legend.position = "right"
  )

ggsave(here("Figures", "map_WEI_eu.pdf"), width = 8, height = 6, dpi = 300)

# --- Factor analysis: parallel test ------------------------------------------
fa.parallel(Z_eu, fa = "fa", n.iter = 100, show.legend = TRUE, main = "")

# --- Factor analysis: one-factor ML model ------------------------------------
fa1_eu <- psych::fa(Z_eu, nfactors = 1, fm = "ml", rotate = "none",
                    scores = "tenBerge")
print(fa1_eu$loadings, digits = 3, cutoff = 0)
print(fa1_eu$communalities)
print(fa1_eu$uniquenesses)

# --- PCA vs FA rank comparison -----------------------------------------------
fa_scores_eu <- as.data.frame(fa1_eu$scores)
fa_scores_eu$country      <- countries
colnames(fa_scores_eu)[1] <- "FA_score"

comparison_eu <- left_join(wei_eu, fa_scores_eu, by = "country") %>%
  mutate(
    WEI      = as.numeric(WEI),
    FA_score = as.numeric(FA_score),
    rank_PCA = rank(-WEI),
    rank_FA  = rank(-FA_score)
  )

cor_pearson_eu  <- cor.test(comparison_eu$WEI, comparison_eu$FA_score,
                            method = "pearson")
cor_spearman_eu <- cor.test(comparison_eu$WEI, comparison_eu$FA_score,
                            method = "spearman")

cat("Pearson r:   ", round(cor_pearson_eu$estimate,  4), "\n")
cat("Spearman rho:", round(cor_spearman_eu$estimate, 4), "\n")

ggplot(comparison_eu, aes(x = rank_PCA, y = rank_FA, label = country)) +
  geom_point(color = "steelblue", size = 3) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "grey40") +
  geom_text(nudge_y = 0.5, size = 3) +
  theme_minimal() +
  labs(
    x = "Rank by PCA (Work Ethic Index)",
    y = "Rank by Factor Analysis"
  ) +
  theme(
    axis.text  = element_text(size = 10),
    axis.title = element_text(size = 10)
  )

ggsave(here("Figures", "pca_fa_eu.pdf"), width = 7, height = 6, dpi = 300)
