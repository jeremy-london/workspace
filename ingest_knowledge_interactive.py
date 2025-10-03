import os
import time
import logging
import argparse
import json
import readline
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from contextlib import contextmanager

# ---------------------------
# Logging Setup
# ---------------------------
logging.Formatter.converter = time.localtime
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()]
)

# ---------------------------
# Tab Completion Setup
# ---------------------------
def complete_file(text, state):
    """Tab completion for file paths - bash style."""
    if state == 0:
        # Get the current line and cursor position
        line = readline.get_line_buffer()
        
        # Check for both "r " and "w " commands
        r_pos = line.find("r ")
        w_pos = line.find("w ")
        
        if r_pos != -1:
            prefix = line[r_pos + 2:]
        elif w_pos != -1:
            prefix = line[w_pos + 2:]
        else:
            readline.matches = []
            return None
        
        # Handle directory completion
        if not prefix:
            prefix = "."
        elif not prefix.startswith("/") and not prefix.startswith("./"):
            prefix = "./" + prefix
        
        # Find matching files
        matches = []
        try:
            # Get directory and filename parts
            dirname = os.path.dirname(prefix)
            basename = os.path.basename(prefix)
            
            if not dirname:
                dirname = "."
            
            # List all files in the directory
            for item in os.listdir(dirname):
                if item.startswith(basename):
                    full_path = os.path.join(dirname, item)
                    if os.path.isdir(full_path):
                        matches.append(item + "/")
                    else:
                        matches.append(item)
            
            # Sort matches
            matches.sort()
            readline.matches = matches
        except (OSError, IOError):
            readline.matches = []
    
    try:
        return readline.matches[state]
    except IndexError:
        return None

# Set up tab completion
readline.set_completer(complete_file)
readline.parse_and_bind("tab: complete")

# ---------------------------
# Logging Suppression Context
# ---------------------------
@contextmanager
def suppress_info_and_error_logs():
    logger = logging.getLogger()
    previous_level = logger.level
    logger.setLevel(logging.CRITICAL + 1)  # Suppress everything up to CRITICAL
    try:
        yield
    finally:
        logger.setLevel(previous_level)


# ---------------------------
# Model Cache Configuration
# ---------------------------
def get_model_cache_dir():
    """Get the Hugging Face cache directory for models."""
    return Path.home() / ".cache" / "huggingface" / "hub"

def is_model_cached_locally(model_name: str) -> bool:
    """Check if model is available in local cache."""
    try:
        cache_dir = get_model_cache_dir()
        model_path = cache_dir / f"models--{model_name.replace('/', '--')}"
        
        if model_path.exists() and any(model_path.iterdir()):
            snapshots_dir = model_path / "snapshots"
            if snapshots_dir.exists() and any(snapshots_dir.iterdir()):
                return True
        return False
    except Exception:
        return False

# ---------------------------
# Resolve Model to use
# ---------------------------
def resolve_embedding_model(model_input: str):
    model_map = {
        "bge-base": ("BAAI/bge-base-en-v1.5", "bge_base_"),
        "bge-large": ("BAAI/bge-large-en-v1.5", "bge_large_"),
        "e5-large": ("intfloat/e5-large-v2", "e5_large_"),
        "bb": ("BAAI/bge-base-en-v1.5", "bge_base_"),
        "bl": ("BAAI/bge-large-en-v1.5", "bge_large_"),
        "e5": ("intfloat/e5-large-v2", "e5_large_")
    }

    return model_map.get(model_input, model_map["bge-base"])  # default fallback


# ---------------------------
# Model-Aware Formatting
# ---------------------------
def format_for_embedding(text: str, model_name: str, mode: str) -> str:
    m = model_name.lower()
    mode = mode.lower()

    if "bge" in m:  # BGE v1.5 base/large
        if mode == "query":
            return f"Represent this sentence for searching relevant passages: {text}"
        else:  # "document"
            return text  # no prefix for passages/documents

    elif "e5" in m:  # E5 family
        if mode == "query":
            return f"query: {text}"
        else:
            return f"passage: {text}"

    return text


# ---------------------------
# Argparse Setup
# ---------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Interactively store, view, and delete natural language facts in"
                                                 " ChromaDB.")
    parser.add_argument("-src", "--source", default="user", help="Optional source tag for metadata")
    parser.add_argument("-load", "--load-file", help="Load data from JSON file on startup")
    parser.add_argument("-em", "--embedding_model", default="bge-base",
                        choices=["bge-base", "bge-large", "e5-large", "bb", "bl", "e5"],
                        help="Embedding model to use: bge-base|bge-large|e5-large or bb|bl|el")
    parser.add_argument("-s", "--schemas", nargs="+", default=['data_mart', 'reporting'],
                        help="Optional list of schemas to include. Use 'all' to include everything.")
    parser.add_argument("--dont-clear", action="store_true", 
                        help="Don't clear ChromaDB on startup (default is to clear)")

    return parser.parse_args()


# ---------------------------
# View Stored Facts
# ---------------------------
def display_stored_facts(collection):
    results = collection.get()
    if not results["ids"]:
        print("ℹ️ \033[31mNo facts stored yet.\033[0m\n")
        return {}

    print("\n\033[32m===\033[0m 📚 \033[32mStored Entries ===\033[0m\n")
    id_map = {}
    for idx, (uid, doc, meta) in enumerate(zip(results["ids"], results["documents"], results["metadatas"]), 1):
        print(f"\033[93m[{idx}]\033[0m 📝 {doc}")
        if meta:
            for key, value in meta.items():
                print(f"📄 \033[36m{key}:\033[0m {value}")
        else:
            print("📄 \033[31mNo metadata available.\033[0m")
        id_map[idx] = uid
        print()  # Add blank line for readability
    print("\033[32m=== End of list ===\033[0m\n")
    return id_map


def get_all_collections_for_type(clear_collections=False):
    models = ["bge-base", "bge-large", "e5-large"]
    client = chromadb.HttpClient(host="chromadb", port=8000)
    collections = []
    with suppress_info_and_error_logs():
        for model in models:
            model_name, prefix = resolve_embedding_model(model)
            
            embedding_fn = SentenceTransformerEmbeddingFunction(model_name=model_name)
            collection = client.get_or_create_collection(
                name=prefix + "imported_data",
                embedding_function=embedding_fn,
                metadata={"hnsw:space": "cosine"}  # cosine for consistency
            )
            
            # Clear collection if requested
            if clear_collections:
                existing_ids = collection.get()["ids"]
                if existing_ids:
                    collection.delete(ids=existing_ids)
                    print(f"🗑️  Cleared {len(existing_ids)} entries from {prefix + 'imported_data'}")
            
            collections.append((collection, model_name))   # <-- return tuple
    return collections


def validate_file_structure(file_data):
    if not isinstance(file_data, list) or len(file_data) == 0:
        print("⚠️ File is empty or not in the expected format (list of entries).")
        return False

    for entry in file_data[:3]:  # Check first few entries for sanity
        if not isinstance(entry, dict):
            print("⚠️ Invalid entry format: not a dictionary.")
            return False
        if "text" not in entry or "metadata" not in entry:
            print("⚠️ Entry missing required fields: 'text' and 'metadata'")
            return False
        if not isinstance(entry.get("metadata"), dict):
            print("⚠️ Invalid metadata format: not a dictionary.")
            return False

    return True


# ---------------------------
# Main Logic
# ---------------------------
def main():
    args = parse_args()
    
    # Show clear startup message based on --dont-clear flag
    if args.dont_clear:
        print("🚀 Starting with persistent database (--dont-clear enabled)...")
    else:
        print("🚀 Starting with fresh database (use --dont-clear to persist data)...")

    if args.embedding_model:
        model_name, prefix = resolve_embedding_model(args.embedding_model)
    else:
        model_name, prefix = resolve_embedding_model("bge-base")

    if args.schemas is None:
        schema_list = ['data_mart', 'reporting']
    elif [s.lower() for s in args.schemas] == ['all']:
        schema_list = None
    else:
        schema_list = args.schemas

    allowed_schemas = [s.strip().lower() for s in schema_list] if schema_list else None

    with suppress_info_and_error_logs():
        embedding_fn = SentenceTransformerEmbeddingFunction(model_name=model_name)
        client = chromadb.HttpClient(host="chromadb", port=8000)
        collection = client.get_or_create_collection(
            name=prefix + "imported_data",
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Clear collection if not using --dont-clear flag
        if not args.dont_clear:
            existing_ids = collection.get()["ids"]
            if existing_ids:
                collection.delete(ids=existing_ids)
                print(f"🗑️  Cleared {len(existing_ids)} entries from {prefix + 'imported_data'}")
            else:
                print("📝 Database is already empty")
        else:
            existing_count = len(collection.get()["ids"])
            if existing_count > 0:
                print(f"📚 Found {existing_count} existing entries in database")
            else:
                print("📝 Database is empty")

    # Load data file on startup if specified
    if args.load_file:
        try:
            filename = args.load_file.strip()
            if not filename.endswith(".json"):
                filename += ".json"

            with open(filename, "r") as f:
                file_data = json.load(f)

            if not validate_file_structure(file_data):
                print("❌ \033[31mAborting import: file structure is invalid or mismatched.\033[0m")
                return

            # Only import to the main collection (the one being queried)
            with suppress_info_and_error_logs():
                # Check if we should clear existing data or append
                if not args.dont_clear:
                    existing_ids = collection.get()["ids"]
                    if existing_ids:
                        collection.delete(ids=existing_ids)
                        print(f"🗑️  Cleared {len(existing_ids)} entries before import")
                
                formatted_docs = [format_for_embedding(entry["text"], model_name, mode="document") for entry
                                  in file_data]
                collection.add(documents=formatted_docs, ids=[entry["id"] for entry in file_data],
                        metadatas=[entry["metadata"] for entry in file_data])
            print(
                f"✅ \033[32mImported {len(file_data)} records to main collection"
                f" for 'imported_data'.\033[0m")

        except Exception as e:
            logging.error(f"❌ \033[31mError reading or processing file '{filename}': {e}\033[0m")
            return

    print("🔁 \033[32mType natural language facts to store.\n"
          "Type '?' to list existing facts. Use '??' for additional details\n"
          "Type '-N' to delete fact N (e.g., -2).\n"
          "Type 'exit' or 'quit' to stop.\n\033[0m")

    id_map = {}

    while True:
        try:
            user_input = input("🧠 \033[35mEnter fact (for fact collection only) or choice:\033[0m ").strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                print("👋 \033[32mExiting...\033[0m")
                break
            elif user_input.startswith("?"):
                table_names_only = False
                n_results = 8
                if len(user_input) > 1 and user_input[1] == "?":
                    longer_version = True
                    n_results = 16  # Show more results for ??
                    query_string = user_input[2:].strip()
                elif len(user_input) > 1 and user_input[1] == "!":
                    longer_version = False
                    table_names_only = True
                    n_results = 16
                    query_string = user_input[2:].strip()
                else:
                    longer_version = False
                    query_string = user_input[1:].strip()

                if not query_string:
                    # List all entries
                    id_map = display_stored_facts(collection)
                    continue

                try:
                    with suppress_info_and_error_logs():
                        formatted_query = format_for_embedding(query_string, model_name, mode="query")
                        results = collection.query(query_texts=[formatted_query], n_results=n_results)

                    raw_ids = results.get("ids", [[]])[0]
                    raw_docs = results.get("documents", [[]])[0]
                    raw_metas = results.get("metadatas", [[]])[0]

                    # Step 1: Filter based on allowed schemas (only if schema field exists)
                    filtered = []
                    for uid, doc, meta in zip(raw_ids, raw_docs, raw_metas):
                        # Only apply schema filtering if the metadata actually contains a schema field
                        if allowed_schemas and allowed_schemas != ["all"] and meta and "schema" in meta:
                            schema = meta.get("schema", "").lower()
                            if not any(schema.endswith(suffix) for suffix in allowed_schemas):
                                continue
                        filtered.append((uid, doc, meta))

                    # Step 2: Print results
                    if not filtered:
                        print("🔍 \033[31mNo matching results found.\033[0m\n")
                    elif table_names_only:
                        print(f"\n\033[32m===\033[0m 🔍 \033[32mTop Matches for '{query_string}': ===\033[0m\n")
                        for idx, (uid, doc, meta) in enumerate(filtered, 1):
                            schema_table = '.'.join(
                                line.split(':', 1)[1].strip().strip('`"') for line in doc.splitlines()[:2])
                            print(f"\033[93m[{idx}]\033[0m 📄 {schema_table}")
                    else:
                        print(f"\n\033[32m===\033[0m 🔍 \033[32mTop Matches for '{query_string}': ===\033[0m\n")
                        for idx, (uid, doc, meta) in enumerate(filtered, 1):
                            print(f"\033[93m[{idx}]\033[0m 📄 {doc}")
                            if longer_version:
                                if meta:
                                    for k, v in meta.items():
                                        if v and v != '[]':
                                            print(f"   \033[36m{k}:\033[0m {v}")
                                    # Show additional details for ??
                                    print(f"   \033[35mID:\033[0m {uid}")
                                else:
                                    print("   \033[31mNo metadata available.\033[0m")
                                    print(f"   \033[35mID:\033[0m {uid}")
                            print()
                except Exception as e:
                    logging.error(f"❌ \033[31mError querying collection: {e}\033[0m")

                continue
            elif user_input.startswith("-"):
                delete_arg = user_input[1:].strip().lower()

                if delete_arg == "all":
                    confirm = input(
                        f"⚠️ Are you sure you want to delete ALL entries from 'imported_data'"
                        f" across all models? (yes/no): ").strip().lower()
                    if confirm == "yes":
                        collections = get_all_collections_for_type(clear_collections=True)
                        with suppress_info_and_error_logs():
                            for col, _ in collections:
                                existing_ids = col.get()["ids"]
                                if existing_ids:
                                    col.delete(ids=existing_ids)
                        print(f"🗑️ \033[32m Cleared all entries from all variants of 'imported_data'.\033[0m")
                    else:
                        print("❌ \033[33mDeletion cancelled.\033[0m")

                    continue
                elif delete_arg.isdigit():
                    idx = int(delete_arg)
                    if idx in id_map:
                        uid = id_map[idx]

                        collections = get_all_collections_for_type(clear_collections=True)
                        with suppress_info_and_error_logs():
                            for col, _ in collections:
                                col.delete(ids=[uid])
                        print(
                            f"🗑️ \033[32mDeleted fact #{idx} from all model variants of 'imported_data'\033[0m")
                        id_map.pop(idx)
                    else:
                        logging.warning(f"⚠️ \033[32mNo fact found with index {idx}. Use '?' to refresh.\033[0m")

                    continue
            elif user_input.lower().startswith("w "):
                # Save full metadata collection to file
                _, filename = user_input.split(" ", 1)
                filename = filename.strip()
                if not filename.endswith(".json"):
                    filename += ".json"

                try:
                    full_data = collection.get()
                    output = []
                    for uid, doc, meta in zip(full_data["ids"], full_data["documents"], full_data["metadatas"]):
                        output.append({
                            "id": uid,
                            "text": doc,
                            "metadata": meta
                        })

                    # Create directory if it doesn't exist
                    file_path = Path(filename)
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(filename, "w") as f:
                        json.dump(output, f, indent=2)
                    print(f"📤 \033[32mExported collection to '{filename}' ({len(output)} records).\033[0m")
                except Exception as e:
                    logging.error(f"❌ \033[31mError writing to file '{filename}': {e}\033[0m")

                continue
            elif user_input.lower().startswith("r "):
                _, filename = user_input.split(" ", 1)
                filename = filename.strip()
                if not filename.endswith(".json"):
                    filename += ".json"

                try:
                    with open(filename, "r") as f:
                        file_data = json.load(f)

                    if not validate_file_structure(file_data):
                        print("❌ \033[31mAborting import: file structure is invalid or mismatched.\033[0m")
                        continue

                    collections = get_all_collections_for_type()

                    with suppress_info_and_error_logs():
                        for col, mname in collections:
                            existing_ids = col.get()["ids"]
                            if existing_ids:
                                col.delete(ids=existing_ids)
                            formatted_docs = [format_for_embedding(entry["text"], mname, mode="document") for entry
                                              in file_data]
                            col.add(documents=formatted_docs, ids=[entry["id"] for entry in file_data],
                                    metadatas=[entry["metadata"] for entry in file_data])
                    print(
                        f"✅ \033[32mImported {len(file_data)} records to all 3 collections"
                        f" for 'imported_data'.\033[0m")

                except Exception as e:
                    logging.error(f"❌ \033[31mError reading or processing file '{filename}': {e}\033[0m")

                continue
            # If not any of the other options, simply take input as fact and store it in 'imported_data'.

            uid = f"fact_{int(time.time() * 1000)}"
            metadata = {
                "source": args.source,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            # Store in the main collection (the one being queried)
            with suppress_info_and_error_logs():
                formatted_text = format_for_embedding(user_input, model_name, mode="document")
                collection.add(documents=[formatted_text], ids=[uid], metadatas=[metadata])
            print(f"✅ \033[32mStored fact:\033[0m {user_input}")

        except KeyboardInterrupt:
            print("\n👋 \033[32mInterrupted by user. Exiting.\033[0m")
            break
        except EOFError:
            print("\n👋 \033[32mEOF detected. Exiting.\033[0m")
            break
        except Exception as e:
            logging.error(f"❌ \033[31mError:\033[0m {e},\n"
                          f"Exception Type: {type(e).__name__}, Line Number: {e.__traceback__.tb_lineno}")


if __name__ == "__main__":
    main()